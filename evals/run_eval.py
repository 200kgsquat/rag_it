import csv
import json
import time
from pathlib import Path
import requests
import os
import re
from dotenv import load_dotenv
from config import Config

load_dotenv()
config = Config()
config.ensure_dirs()

QUESTIONS_CSV = config.base_dir / "evals" / "questions.csv"
RESULTS_DIR = config.base_dir / "evals" / "results"
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

API_URL = os.getenv("RAG_API_URL", "http://localhost:8000/ask")
GROQ_API_URL = os.getenv("GROQ_API_URL", "https://api.groq.com/openai/v1/chat/completions")


def load_questions(path: Path):
    with path.open("r", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def call_api(question: str):
    t0 = time.time()
    try:
        r = requests.post(API_URL, json={"question": question}, timeout=30)
        r.raise_for_status()
        data = r.json()
        data["latency_ms"] = int((time.time() - t0) * 1000)
        return data
    except requests.exceptions.ConnectionError as e:
        return {"error": f"Connection error: {str(e)}", "latency_ms": None}
    except requests.exceptions.Timeout as e:
        return {"error": f"Timeout error: {str(e)}", "latency_ms": None}
    except requests.exceptions.HTTPError as e:
        return {"error": f"HTTP error {r.status_code}: {str(e)}", "latency_ms": None}
    except requests.RequestException as e:
        return {"error": f"Request error: {str(e)}", "latency_ms": None}
    except Exception as e:
        return {"error": f"Unexpected error: {str(e)}", "latency_ms": None}


def judge_with_groq(question: str, answer: str):
    key = os.getenv("JUDGER_LLM_MODEL_API_KEY", os.getenv("GROQ_API_KEY"))
    if not key:
        return {"score": None, "explain": "No API key set (JUDGER_LLM_MODEL_API_KEY or GROQ_API_KEY)"}

    headers = {"Authorization": f"Bearer {key}", "Content-Type": "application/json"}

    judge_prompt = f"""You are an expert evaluator of IT support Q&A systems.

Rate the quality of this answer on a scale of 0-5:

Question: {question}
Answer: {answer}

Rating criteria:
- 5: Excellent - Complete, accurate, practical, well-structured
- 4: Good - Mostly complete and accurate with minor issues
- 3: Fair - Partially correct but missing key details or slightly inaccurate
- 2: Poor - Major gaps, mostly unhelpful
- 1: Very Poor - Wrong information or misleading
- 0: No Answer - No useful information, just "I don't know"

Focus on: accuracy, completeness, helpfulness, clarity, and practicality for IT support.

IMPORTANT: Respond ONLY with valid JSON. No explanations, no thinking, no extra text. Format: {{"score": 4, "explanation": "brief reason"}}"""

    payload = {
        "model": config.judger.model,
        "messages": [{"role": "user", "content": judge_prompt}],
        "temperature": config.judger.temperature,
        "max_tokens": config.judger.max_tokens,
    }

    try:
        r = requests.post(GROQ_API_URL, headers=headers, json=payload, timeout=30)
        r.raise_for_status()

        response_data = r.json()
        text = response_data.get("choices", [{}])[0].get("message", {}).get("content", "")

        if not text:
            return {"score": None, "explain": "No content in response"}

        try:
            result = json.loads(text)
                             
            if "score" not in result:
                return {"score": None, "explain": "No score in response"}
            if not isinstance(result["score"], (int, float)):
                return {"score": None, "explain": "Invalid score type"}
            if not (0 <= result["score"] <= 5):
                return {"score": None, "explain": f"Score out of range: {result['score']}"}
            
                                   
            normalized_result = {"score": result["score"]}
            if "explanation" in result:
                normalized_result["explain"] = result["explanation"]
            elif "explain" in result:
                normalized_result["explain"] = result["explain"]
            else:
                normalized_result["explain"] = "No explanation provided"
            
            return normalized_result
        except json.JSONDecodeError:
            
                                                            
            score_match = re.search(r'"score"\s*:\s*(\d+)', text)
            explain_match = re.search(r'"explanation"\s*:\s*"([^"]*)"', text)
            
            if score_match:
                score = int(score_match.group(1))
                if 0 <= score <= 5:
                    explanation = explain_match.group(1) if explain_match else "Score extracted from text"
                    return {"score": score, "explain": explanation}
            
                                                
            number_match = re.search(r'\b(\d+)\b', text)
            if number_match:
                score = int(number_match.group(1))
                if 0 <= score <= 5:
                                                              
                    explanation = text[:200] + "..." if len(text) > 200 else text
                    return {"score": score, "explain": f"Score found in text: {explanation}"}
            
            return {"score": None, "explain": "Could not extract valid score"}

    except requests.exceptions.RequestException as e:
        return {"score": None, "explain": f"Request error: {str(e)}"}
    except Exception as e:
        return {"score": None, "explain": f"Unexpected error: {str(e)}"}


def recall_at_k(sources, gold, k=3):
    """Calculate recall@k by checking if any of the top-k sources match the gold path."""
    if not sources or not gold:
        return 0

                                                                               
    gold_filename = Path(str(gold)).name.lower()
    gold_base = gold_filename.rsplit('.', 1)[0] if '.' in gold_filename else gold_filename
    
                                                                                            
    gold_number = gold_base.split('_')[0] if '_' in gold_base else None

    for source in sources[:k]:
        source_path = str(source.get("path", ""))
        if not source_path:
            continue

                                           
        source_filename = Path(source_path).name.lower()
        source_base = source_filename.rsplit('.', 1)[0] if '.' in source_filename else source_filename
        source_number = source_base.split('_')[0] if '_' in source_base else None

                                                
        if source_filename == gold_filename:
            return 1

                                                                
        if source_base == gold_base:
            return 1

                                                            
        if gold_number and source_number and gold_number == source_number:
            return 1

                                                                                                   
        if gold_base.startswith(source_base) or source_base.startswith(gold_base):
            return 1

                                                    
        gold_words = set(gold_base.replace('_', ' ').split())
        source_words = set(source_base.replace('_', ' ').split())
        
                                                            
        if gold_words and source_words:
            common_words = gold_words.intersection(source_words)
            similarity = len(common_words) / max(len(gold_words), len(source_words))
            if similarity > 0.5:
                return 1

    return 0


def run_eval():
    questions = load_questions(QUESTIONS_CSV)
    total_questions = len(questions)
    results = []
    
    print(f"🚀 Starting evaluation of {total_questions} questions...")
    print(f"📊 API URL: {API_URL}")
    print(f"🤖 Judge API: {'Enabled' if os.getenv('GROQ_API_KEY') else 'Disabled (no GROQ_API_KEY)'}")
    print("-" * 50)
    
    for i, q in enumerate(questions, 1):
        question, gold = q.get("question"), q.get("gold_path")
        if not question or not gold:
            print(f"⚠️  Skipping question {i}: missing question or gold_path")
            continue
            
        print(f"[{i}/{total_questions}] Evaluating: {question[:60]}{'...' if len(question) > 60 else ''}")
        
                   
        res = call_api(question)
        if res.get("error"):
            print(f"❌ API Error: {res['error']}")
            results.append({
                "question": question, 
                "gold": gold, 
                "error": res,
                "recall_at_3": 0,
                "latency_ms": res.get("latency_ms"),
                "judge": {"score": None, "explain": "API error"}
            })
            continue
            
        answer = res.get("answer") or str(res)
        sources = res.get("sources", [])
        recall = recall_at_k(sources, gold)
        
        print(f"   📝 Answer: {answer[:100]}{'...' if len(answer) > 100 else ''}")
        print(f"   📚 Sources: {len(sources)} found")
        print(f"   🎯 Recall@3: {'✅' if recall else '❌'}")
        if not recall and sources:
            gold_filename = Path(str(gold)).name
            source_filenames = [Path(s.get("path", "")).name for s in sources[:3]]
            print(f"   🔍 Gold: {gold_filename}")
            print(f"   🔍 Sources: {source_filenames}")
        print(f"   ⏱️  Latency: {res.get('latency_ms', 'N/A')}ms")
        
                               
        judge_result = judge_with_groq(question, answer)
        if judge_result.get("score") is not None:
            print(f"   ⭐ Judge Score: {judge_result['score']}/5")
        else:
            print(f"   ⭐ Judge: {judge_result.get('explain', 'N/A')}")

                                        
        time.sleep(5)                                      
        
        record = {
            "question": question,
            "gold": gold,
            "answer": answer,
            "sources": sources,
            "recall_at_3": recall,
            "latency_ms": res.get("latency_ms"),
            "judge": judge_result,
        }
        results.append(record)
        
                                              
        (RESULTS_DIR / "latest.json").write_text(json.dumps(results, ensure_ascii=False, indent=2))
        print()
    
                          
    timestamp = int(time.time())
    final_file = RESULTS_DIR / f"results_{timestamp}.json"
    final_file.write_text(json.dumps(results, ensure_ascii=False, indent=2))
    
                
    successful_results = [r for r in results if not r.get('error')]
    total_recall = sum(r.get("recall_at_3", 0) for r in successful_results)
    recall_percentage = (total_recall / len(successful_results) * 100) if successful_results else 0
    avg_latency = sum(r.get("latency_ms", 0) for r in results if r.get("latency_ms")) / max(1, len([r for r in results if r.get("latency_ms")]))
    judge_scores = [r.get("judge", {}).get("score") for r in results if r.get("judge", {}).get("score") is not None]
    avg_judge_score = sum(judge_scores) / len(judge_scores) if judge_scores else None
    
    print("=" * 50)
    print("📊 EVALUATION COMPLETE")
    print(f"✅ Total questions: {len(results)}")
    print(f"✅ Successful questions: {len(successful_results)}")
    print(f"❌ Failed questions: {len(results) - len(successful_results)}")
    print(f"🎯 Recall@3: {total_recall}/{len(successful_results)} ({recall_percentage:.1f}%)")
    print(f"⏱️  Average latency: {avg_latency:.0f}ms")
    if avg_judge_score is not None:
        print(f"⭐ Average judge score: {avg_judge_score:.2f}/5")
    print(f"💾 Results saved to: {final_file}")
    print("✅ Done.")


if __name__ == "__main__":
    run_eval()
