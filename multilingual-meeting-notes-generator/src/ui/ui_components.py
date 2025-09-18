"""UI components for displaying meeting results."""

import streamlit as st
from typing import List
from src.data.data_models import MeetingResult, Speaker, ActionItem


def display_meeting_header(result: MeetingResult) -> None:
    """Display the main meeting header with key metrics."""
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Duration", f"{result.duration // 60}m {result.duration % 60}s")
    
    with col2:
        st.metric("Speakers", len(result.speakers))
    
    with col3:
        st.metric("Action Items", len(result.action_items))


def display_meeting_summary(summary: str) -> None:
    """Display the generated meeting summary with clear formatting."""
    st.markdown('<h2 style="color: #1C59C3; margin-bottom: 1px; font-size: 28px;">📝 Meeting Summary</h2>', unsafe_allow_html=True)
    
    # Process the summary to style essential headings and fix line breaks
    import re
    
    # Style only the essential headings: Topics Discussed, Key Decisions, Next Steps
    essential_headings = ['Topics Discussed', 'Key Decisions', 'Next Steps']
    
    enhanced_summary = summary
    for heading in essential_headings:
        enhanced_summary = re.sub(
            rf'\*\*{re.escape(heading)}:\*\*', 
            f'<h3 style="color: #FFFFFF; font-size: 22px; margin-top: 2px; margin-bottom: 1px; font-weight: 600;">{heading}:</h3>', 
            enhanced_summary
        )
    
    # Convert bullet points to proper HTML list elements
    # Split by sections and process each section
    sections = enhanced_summary.split('\n\n')
    processed_sections = []
    
    for section in sections:
        if section.strip():
            # Check if this section has bullet points
            lines = section.split('\n')
            processed_lines = []
            in_list = False
            
            for line in lines:
                line = line.strip()
                if line.startswith('• '):
                    # This is a bullet point
                    if not in_list:
                        processed_lines.append('<ul style="margin: 8px 0; padding-left: 20px;">')
                        in_list = True
                    # Remove the bullet symbol and add as list item
                    content = line[2:].strip()  # Remove '• ' prefix
                    processed_lines.append(f'<li style="margin: 4px 0; color: #FFFFFF;">{content}</li>')
                else:
                    # This is not a bullet point
                    if in_list:
                        processed_lines.append('</ul>')
                        in_list = False
                    if line:  # Only add non-empty lines
                        processed_lines.append(f'<div style="margin: 8px 0; color: #FFFFFF;">{line}</div>')
            
            # Close any open list
            if in_list:
                processed_lines.append('</ul>')
            
            processed_sections.append('\n'.join(processed_lines))
    
    # Join sections back together
    final_summary = '\n\n'.join(processed_sections)
    
    # Display summary with better typography
    st.markdown(f"""
    <div style="font-size: 16px; line-height: 1.4; color: #FFFFFF; margin-bottom: 20px;">
        {final_summary}
    </div>
    """, unsafe_allow_html=True)


def display_speaker_analysis(speakers: List[Speaker], segments) -> None:
    """Display speaker information and what they said."""
    st.markdown('<h2 style="color: #1C59C3; margin-bottom: 1px; font-size: 28px;">👥 Speaker Diarization</h2>', unsafe_allow_html=True)
    
    if not speakers:
        st.info("No speaker information available.")
        return
    
    # Display speakers with all their statements
    for speaker in speakers:
        speaking_time = f"{speaker.speaking_time // 60}m {speaker.speaking_time % 60}s"
        st.write(f"**{speaker.name}** - {speaking_time} ({speaker.word_count} words)")
        
        # Show all what this speaker said
        speaker_segments = [segment for segment in segments if segment.speaker_id == speaker.id]
        
        if speaker_segments:
            with st.expander(f"View all statements from {speaker.name}", expanded=False):
                for i, segment in enumerate(speaker_segments, 1):
                    timestamp = f"{segment.start_time // 60000:02d}:{segment.start_time // 1000 % 60:02d}"
                    
                    st.write(f"**Statement {i}** ({timestamp}):")
                    st.write(f"  {segment.text}")
                    if segment.confidence < 0.7:
                        st.caption(f"*Low confidence: {segment.confidence:.2f}*")
                    st.write("")
        else:
            st.write("  *No statements found*")
        


def display_action_items(action_items: List[ActionItem]) -> None:
    """Display action items organized by assignee with clean, elegant styling."""
    st.markdown('<h2 style="color: #1C59C3; margin-bottom: 1px; font-size: 28px;">✅ Action Items</h2>', unsafe_allow_html=True)
    
    if not action_items:
        st.info("No action items were identified in this meeting.")
        return
    
    # Group by assignee
    by_person = {}
    unassigned = []
    
    for item in action_items:
        if item.assignee:
            if item.assignee not in by_person:
                by_person[item.assignee] = []
            by_person[item.assignee].append(item)
        else:
            unassigned.append(item)
    
    # Show each person's items with clean styling
    for person, items in by_person.items():
        # Simple person header
        st.markdown(f'<h3 style="color: #FFFFFF; font-size: 20px; margin-bottom: 1px; margin-top: 2px;">👤 {person}</h3>', unsafe_allow_html=True)
        
        # Action items for this person
        for i, item in enumerate(items, 1):
            details = []
            if item.due_date:
                details.append(f"Due: {item.due_date}")
            if item.priority:
                details.append(f"Priority: {item.priority.title()}")
            
            details_text = f" • {', '.join(details)}" if details else ""
            
            st.markdown(f"""
            <div style="margin-bottom: 16px; padding-left: 16px; border-left: 3px solid #1C59C3;">
                <div style="color: #FFFFFF; font-size: 16px; line-height: 1.5; margin-bottom: 4px;">
                    <strong>{i}.</strong> {item.description}
                </div>
                {f'<div style="color: #CCCCCC; font-size: 14px; margin-top: 4px;">{details_text}</div>' if details_text else ''}
            </div>
            """, unsafe_allow_html=True)
    
    # Show unassigned items
    if unassigned:
        st.markdown('<h3 style="color: #FFFFFF; font-size: 20px; margin-bottom: 1px; margin-top: 2px;">📋 Unassigned</h3>', unsafe_allow_html=True)
        
        for i, item in enumerate(unassigned, 1):
            details = []
            if item.due_date:
                details.append(f"Due: {item.due_date}")
            if item.priority:
                details.append(f"Priority: {item.priority.title()}")
            
            details_text = f" • {', '.join(details)}" if details else ""
            
            st.markdown(f"""
            <div style="margin-bottom: 16px; padding-left: 16px; border-left: 3px solid #6C757D;">
                <div style="color: #FFFFFF; font-size: 16px; line-height: 1.5; margin-bottom: 4px;">
                    <strong>{i}.</strong> {item.description}
                </div>
                {f'<div style="color: #CCCCCC; font-size: 14px; margin-top: 4px;">{details_text}</div>' if details_text else ''}
            </div>
            """, unsafe_allow_html=True)


def display_meeting_transcript(segments, language: str = "en", result=None) -> None:
    """Display the meeting transcript with enhanced formatting."""
    st.markdown('<h2 style="color: #1C59C3; margin-bottom: 1px; font-size: 28px;">📄 Meeting Transcript</h2>', unsafe_allow_html=True)
    
    if not segments:
        st.info("No transcript is available for this meeting.")
        return
    
    # Add transcript controls
    col1, col2, col3 = st.columns([1, 1, 4])
    
    with col1:
        show_timestamps = st.checkbox("Show timestamps", value=True)
    
    with col2:
        show_confidence = st.checkbox("Show confidence", value=False)
    
    st.markdown("---")
    
    # Display as continuous text
    full_text = ""
    for segment in segments:
        timestamp = f"{segment.start_time // 60000:02d}:{segment.start_time // 1000 % 60:02d}"
        
        speaker_info = f"**{segment.speaker_id}**"
        if show_timestamps:
            speaker_info += f" ({timestamp})"
        if show_confidence:
            speaker_info += f" [Confidence: {segment.confidence:.2f}]"
        
        full_text += f"{speaker_info}: {segment.text}\n\n"
    
    st.markdown(
        f"""
        <div style="background-color: #262730; padding: 15px; border-radius: 8px; max-height: 400px; overflow-y: auto;">
            <pre style="white-space: pre-wrap; font-family: sans-serif; font-size: 14px; line-height: 1.6; color: white;">{full_text}</pre>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    # Add spacing before statistics
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Add summary statistics
    st.markdown('<h2 style="color: #1C59C3; margin-bottom: 1px; font-size: 28px;">📊 Transcript Statistics</h2>', unsafe_allow_html=True)
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Segments", len(segments))
    
    with col2:
        if result:
            st.metric("Total Words", result.total_words)
        else:
            st.metric("Total Words", sum(len(segment.text.split()) for segment in segments))
    
    with col3:
        if result:
            st.metric("Avg Confidence", f"{result.avg_confidence:.2f}")
        else:
            avg_conf = len(segments) and sum(segment.confidence for segment in segments) / len(segments) or 0
            st.metric("Avg Confidence", f"{avg_conf:.2f}")
    
    with col4:
        if result:
            st.metric("Unique Speakers", result.unique_speakers_count)
        else:
            unique_speakers = len(set(segment.speaker_id for segment in segments))
            st.metric("Unique Speakers", unique_speakers)


