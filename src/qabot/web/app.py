import streamlit as st
import requests
import uuid
import os
from datetime import datetime

API_URL = os.getenv("API_URL")

def init_session():
    """Initialize session state variables"""
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    if "history_summary" not in st.session_state:
        st.session_state.history_summary = ""
    if "show_sources" not in st.session_state:
        st.session_state.show_sources = False
    if "session_id" not in st.session_state:
        st.session_state.session_id = str(uuid.uuid4())
    if "message_count" not in st.session_state:
        st.session_state.message_count = 0
    if "processing" not in st.session_state:
        st.session_state.processing = False

def get_last_turns():
    """Get the 2 most recent question-answer pairs (4 messages total)"""
    if len(st.session_state.chat_history) >= 4:
        return st.session_state.chat_history[-4:]
    return st.session_state.chat_history

def call_summarize_endpoint():
    """Call the separate summarize endpoint to update conversation summary"""
    try:
        response = requests.post(
            f"{API_URL}/summarize",
            json={
                "session_id": st.session_state.session_id,
                "chat_history": st.session_state.chat_history,
                "current_summary": st.session_state.history_summary
            },
            timeout=30
        )
        if response.status_code == 200:
            data = response.json()
            return data.get("summary", "")
        else:
            st.error(f"Summary update failed: {response.status_code}")
            return st.session_state.history_summary
    except Exception as e:
        st.error(f"Summary request failed: {e}")
        return st.session_state.history_summary

def update_conversation_summary():
    """Update summary every 4 messages (configurable)"""
    SUMMARY_UPDATE_FREQUENCY = 4
    
    if (len(st.session_state.chat_history) > 0 and 
        st.session_state.message_count % SUMMARY_UPDATE_FREQUENCY == 0 and
        st.session_state.message_count > 0):
        
        with st.spinner("Updating conversation summary..."):
            new_summary = call_summarize_endpoint()
            st.session_state.history_summary = new_summary

def clean_response_content(content):
    """Clean up problematic response content"""
    if not content:
        return "No response received"
    
                                                     
    lines = content.split('\n')
    cleaned_lines = []
    
    for line in lines:
                                               
        if line.count('*') > 10 or line.count('Reply') > 5:
            continue
                                               
        if line.strip() and not line.startswith('[') and not line.endswith(']'):
            cleaned_lines.append(line.strip())
    
    cleaned_content = '\n'.join(cleaned_lines)
    
                                                         
    if len(cleaned_content) < 10 or 'Reply * Reply *' in cleaned_content:
        return "I apologize, but I'm having trouble generating a proper response. Please try rephrasing your question."
    
    return cleaned_content

def format_sources(sources):
    """Format sources with proper fallbacks for missing data"""
    if not sources:
        return []
    
    formatted_sources = []
    for source in sources[:3]:                        
                                     
        title = source.get('title', '')
        if not title:
                                                      
            path = source.get('path', '')
            if path:
                title = path.split('/')[-1] if '/' in path else path
            else:
                title = 'Unknown document'
        
                                           
        updated = source.get('updated_at', source.get('updated', ''))
        if not updated:
            updated = 'Date not available'
        
        formatted_sources.append({
            'title': title,
            'updated': updated
        })
    
    return formatted_sources

def display_chat():
    """Display chat messages with optional sources"""
    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]):
                                     
            content = msg["content"]
            if msg["role"] == "assistant":
                content = clean_response_content(content)
            st.markdown(content)
            
                                                                        
            if (st.session_state.show_sources and 
                msg["role"] == "assistant" and 
                "sources" in msg):
                
                sources = format_sources(msg.get("sources", []))
                if sources:
                    st.markdown("**Sources:**")
                    for source in sources:
                        st.caption(f"• {source['title']} (Updated: {source['updated']})")

def handle_chat():
    """Handle user input and get response from RAG model"""
    if user_input := st.chat_input("Enter your message..."):
                                                
        if st.session_state.processing:
            st.warning("Please wait for the current response to complete.")
            return
            
        st.session_state.processing = True
        
                                          
        user_message = {
            "role": "user", 
            "content": user_input,
            "timestamp": datetime.now().isoformat()
        }
        st.session_state.chat_history.append(user_message)
        st.session_state.message_count += 1
        
                                                   
        payload = {
            "session_id": st.session_state.session_id,
            "history_summary": st.session_state.history_summary,
            "last_turns": get_last_turns(),
            "question": user_input
        }
        
                                                  
        assistant_placeholder = st.empty()
        
        try:
            with st.spinner("Thinking..."):
                response = requests.post(
                    f"{API_URL}/ask",
                    json=payload,
                    timeout=30
                )
                
            if response.status_code == 200:
                data = response.json()
                
                                            
                answer_content = clean_response_content(data.get("answer", ""))
                sources = format_sources(data.get("sources", []))
                
                                                        
                assistant_message = {
                    "role": "assistant",
                    "content": answer_content,
                    "sources": sources,
                    "timestamp": datetime.now().isoformat()
                }
                st.session_state.chat_history.append(assistant_message)
                st.session_state.message_count += 1
                
                                                          
                update_conversation_summary()
                
            else:
                error_msg = f"Error {response.status_code}: {response.text}"
                st.session_state.chat_history.append({
                    "role": "assistant",
                    "content": error_msg,
                    "sources": []
                })
                st.session_state.message_count += 1
                
        except requests.exceptions.Timeout:
            error_msg = "Request timeout. Please try again."
            st.session_state.chat_history.append({
                "role": "assistant",
                "content": error_msg,
                "sources": []
            })
            st.session_state.message_count += 1
        except Exception as e:
            error_msg = f"Request failed: {str(e)}"
            st.session_state.chat_history.append({
                "role": "assistant", 
                "content": error_msg,
                "sources": []
            })
            st.session_state.message_count += 1
        finally:
            st.session_state.processing = False
            st.rerun()

def reset_chat():
    """Reset the chat session completely"""
    st.session_state.chat_history = []
    st.session_state.history_summary = ""
    st.session_state.message_count = 0
    st.session_state.session_id = str(uuid.uuid4())
    st.session_state.processing = False
    st.rerun()

def main():
    """Main application function"""
    st.set_page_config(
        page_title="QA Chat Interface", 
        page_icon="💬",
        layout="wide"
    )
    
    st.title("💬 QA Chat Interface")
    st.caption("Chat with your RAG model - Context preserved across 10-15 messages")
    
                              
    init_session()
    
                   
    col1, col2, col3 = st.columns([1, 1, 2])
    
    with col1:
        if st.button("🔄 Reset Chat", use_container_width=True):
            reset_chat()
    
    with col2:
        st.session_state.show_sources = st.toggle(
            "Show Sources", 
            value=st.session_state.show_sources,
            help="Toggle to show/hide source citations"
        )
    
    with col3:
        if st.session_state.history_summary:
            st.caption(f"**Conversation Summary:** {st.session_state.history_summary}")
        else:
            st.caption("**Conversation Summary:** No summary yet")
    
                           
    display_chat()
    
                               
    if st.session_state.processing:
        with st.chat_message("assistant"):
            st.markdown("Thinking...")
    
                       
    handle_chat()
    
                                                      
    with st.expander("Debug Information", expanded=False):
        st.write(f"Session ID: {st.session_state.session_id}")
        st.write(f"Message count: {st.session_state.message_count}")
        st.write(f"Chat history length: {len(st.session_state.chat_history)}")
        st.write(f"Processing: {st.session_state.processing}")
        if st.session_state.chat_history:
            recent_history = st.session_state.chat_history[-4:] if len(st.session_state.chat_history) >= 4 else st.session_state.chat_history
            st.json(recent_history)

if __name__ == "__main__":
    main()