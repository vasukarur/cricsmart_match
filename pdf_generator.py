"""
PDF Generator for Cricket Scoreboard
Generates professional PDF reports with scoreboard and summary tabs
"""

import os
import tempfile
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT


class CricketScoreboardPDF:
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self.setup_custom_styles()
    
    def setup_custom_styles(self):
        """Setup custom styles for PDF formatting"""
        # Title style
        self.title_style = ParagraphStyle(
            'CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=20,
            spaceAfter=30,
            alignment=TA_CENTER,
            textColor=colors.darkblue
        )
        
        # Header style
        self.header_style = ParagraphStyle(
            'CustomHeader',
            parent=self.styles['Heading2'],
            fontSize=16,
            spaceAfter=12,
            textColor=colors.darkblue
        )
        
        # Normal text style
        self.normal_style = ParagraphStyle(
            'CustomNormal',
            parent=self.styles['Normal'],
            fontSize=10,
            spaceAfter=6
        )
        
        # Small text style
        self.small_style = ParagraphStyle(
            'CustomSmall',
            parent=self.styles['Normal'],
            fontSize=8,
            spaceAfter=3
        )
    
    def generate_scoreboard_pdf(self, match_data, output_path=None):
        """Generate complete scoreboard PDF with scoreboard and summary tabs"""
        
        if not output_path:
            # Create temporary file
            temp_dir = tempfile.gettempdir()
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = os.path.join(temp_dir, f"cricket_scoreboard_{timestamp}.pdf")
        
        # Create PDF document
        doc = SimpleDocTemplate(output_path, pagesize=A4)
        story = []
        
        # Add scoreboard section
        self._add_scoreboard_section(story, match_data)
        
        # Add page break for summary
        story.append(PageBreak())
        
        # Add summary section
        self._add_summary_section(story, match_data)
        
        # Build PDF
        doc.build(story)
        
        return output_path
    
    def _add_scoreboard_section(self, story, match_data):
        """Add scoreboard section to PDF"""
        
        # Title
        match_name = match_data.get('match_name', 'Cricket Match')
        title = Paragraph(match_name.upper(), self.title_style)
        story.append(title)
        story.append(Spacer(1, 20))
        
        # Match Information
        match_info = match_data.get('match')
        if not match_info:
            story.append(Paragraph("No match data available", self.normal_style))
            return
        
        # Debug match completion status
        print(f"DEBUG PDF: Match completion check:")
        print(f"  - has first_innings_summary: {hasattr(match_info, 'first_innings_summary')}")
        print(f"  - first_innings_summary value: {getattr(match_info, 'first_innings_summary', None)}")
        print(f"  - current_innings: {getattr(match_info, 'current_innings', None)}")
        print(f"  - is_innings_complete(): {match_info.is_innings_complete() if hasattr(match_info, 'is_innings_complete') else 'N/A'}")
        print(f"  - is_match_complete(): {match_info.is_match_complete() if hasattr(match_info, 'is_match_complete') else 'N/A'}")
        print(f"  - get_match_winner(): {match_info.get_match_winner() if hasattr(match_info, 'get_match_winner') else 'N/A'}")
        print(f"  - match_data keys: {list(match_data.keys())}")
        print(f"  - match_winner from match_data: {match_data.get('match_winner', 'N/A')}")
        
        team_a = getattr(match_info, 'team_a', None)
        team_b = getattr(match_info, 'team_b', None)
        
        if team_a and team_b:
            # Match header table
            match_header_data = [
                ["Match Information", ""],
                ["Team A:", getattr(team_a, 'team_name', "Team A")],
                ["Team B:", getattr(team_b, 'team_name', "Team B")],
                ["Overs:", str(getattr(match_info, 'max_overs', 0))],
                ["Date:", datetime.now().strftime("%d/%m/%Y %H:%M")],
                ["Status:", "COMPLETED" if (hasattr(match_info, 'is_match_complete') and match_info.is_match_complete()) else "IN PROGRESS"],
            ["🏆 Winner:", match_info.get_match_winner() if (hasattr(match_info, 'is_match_complete') and match_info.is_match_complete() and hasattr(match_info, 'get_match_winner')) else match_data.get('match_winner', 'N/A')],
            ]
            
            match_table = Table(match_header_data, colWidths=[2*inch, 3*inch])
            match_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            story.append(match_table)
            story.append(Spacer(1, 20))
        
        # Current Score
        current_score = self._format_current_score(match_info)
        score_paragraph = Paragraph(f"<b>Current Score:</b> {current_score}", self.header_style)
        story.append(score_paragraph)
        story.append(Spacer(1, 15))
        
        # Batting Scorecard
        if team_a:
            self._add_batting_scorecard(story, team_a, "Team A Batting")
        
        if team_b:
            self._add_batting_scorecard(story, team_b, "Team B Batting")
        
        # Bowling Figures
        if team_a:
            self._add_bowling_figures(story, team_a, "Team A Bowling", match_data)
        if team_b:
            self._add_bowling_figures(story, team_b, "Team B Bowling", match_data)
    
    def _add_summary_section(self, story, match_data):
        """Add summary section to PDF"""
        
        # Title
        match_name = match_data.get('match_name', 'Cricket Match')
        title = Paragraph(f"{match_name} - MATCH SUMMARY", self.title_style)
        story.append(title)
        story.append(Spacer(1, 20))
        
        match_info = match_data.get('match')
        if not match_info:
            story.append(Paragraph("No match data available", self.normal_style))
            return
        
        # Match Summary
        summary_data = [
            ["Match Summary", ""],
            ["Total Runs:", str(getattr(match_info, 'total_runs', 0))],
            ["Total Wickets:", str(getattr(match_info, 'wickets', 0))],
            ["Overs Completed:", f"{getattr(match_info, 'current_over', 0)}.{getattr(match_info, 'current_ball', 0)}"],
            ["Batting First:", getattr(match_info, 'batting_first_team_name', 'N/A')],
        ]
        
        # Add innings and match status
        innings_status = "COMPLETED" if (hasattr(match_info, 'is_innings_complete') and match_info.is_innings_complete()) else "IN PROGRESS"
        match_status = "COMPLETED" if (hasattr(match_info, 'is_match_complete') and match_info.is_match_complete()) else "IN PROGRESS"
        
        summary_data.append(["Innings Status:", innings_status])
        summary_data.append(["Match Status:", match_status])
        
        # Add winner if match is complete
        if (hasattr(match_info, 'is_match_complete') and match_info.is_match_complete()):
            winner = match_info.get_match_winner() if hasattr(match_info, 'get_match_winner') else match_data.get('match_winner', 'N/A')
            summary_data.append(["🏆 Match Winner:", winner])
            
            # Add Man of the Match
            player_of_match = match_data.get('player_of_match')
            print(f"DEBUG PDF: Player of the Match data: {player_of_match}")
            
            if player_of_match:
                motm_name = player_of_match.get('name', 'N/A')
                motm_team = player_of_match.get('team', 'N/A')
                summary_data.append(["🏆 Man of the Match:", f"{motm_name} ({motm_team})"])
            else:
                # Fallback to match_result if available
                match_result = match_data.get('match_result', {})
                print(f"DEBUG PDF: Match result data: {match_result}")
                
                # Check multiple possible Man of the Match field names
                man_of_match = (match_result.get('man_of_match') or 
                               match_result.get('player_of_match') or 
                               match_result.get('man_of_the_match') or 
                               match_result.get('motm') or 
                               match_result.get('MOTM') or 
                               match_result.get('playerOfMatch'))
                
                print(f"DEBUG PDF: Man of the Match found: {man_of_match}")
                
                # If it's an object, extract the name
                if man_of_match and isinstance(man_of_match, dict):
                    man_of_match = (man_of_match.get('name') or 
                                  man_of_match.get('player_name') or 
                                  man_of_match.get('player') or 
                                  man_of_match.get('fullName') or 
                                  man_of_match.get('full_name') or 
                                  str(man_of_match))
                
                # If still not found, try to determine from top performers
                if not man_of_match:
                    top_batsmen_a = match_data.get('top_batsmen_a', [])
                    top_batsmen_b = match_data.get('top_batsmen_b', [])
                    top_bowlers_a = match_data.get('top_bowlers_a', [])
                    top_bowlers_b = match_data.get('top_bowlers_b', [])
                    
                    if top_batsmen_a and len(top_batsmen_a) > 0:
                        man_of_match = top_batsmen_a[0].get('name', 'N/A')
                    elif top_batsmen_b and len(top_batsmen_b) > 0:
                        man_of_match = top_batsmen_b[0].get('name', 'N/A')
                    elif top_bowlers_a and len(top_bowlers_a) > 0:
                        man_of_match = top_bowlers_a[0].get('name', 'N/A')
                    elif top_bowlers_b and len(top_bowlers_b) > 0:
                        man_of_match = top_bowlers_b[0].get('name', 'N/A')
                
                summary_data.append(["🏆 Man of the Match:", man_of_match or 'Not awarded'])
        
        # Add first innings summary if available
        first_innings = getattr(match_info, 'first_innings_summary', None)
        if first_innings:
            summary_data.append(["1st Innings Score:", f"{first_innings.get('runs', 0)}/{first_innings.get('wickets', 0)} in {first_innings.get('overs', '0.0')} overs"])
            summary_data.append(["1st Innings Team:", first_innings.get('team', 'N/A')])
        
        # Add current innings score
        summary_data.append(["Current Innings Score:", f"{getattr(match_info, 'total_runs', 0)}/{getattr(match_info, 'wickets', 0)} in {getattr(match_info, 'current_over', 0)}.{getattr(match_info, 'current_ball', 0)} overs"])
        
        summary_table = Table(summary_data, colWidths=[2*inch, 3*inch])
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        story.append(summary_table)
        story.append(Spacer(1, 20))
        
        # Key Events
        events = getattr(match_info, 'events', [])
        print(f"DEBUG PDF: Total events found: {len(events)}")
        
        if events:
            story.append(Paragraph("KEY EVENTS", self.header_style))
            story.append(Spacer(1, 10))
            
            # Show last 20 events instead of 10
            recent_events = events[-20:] if len(events) > 20 else events
            
            event_data = [["Over", "Ball", "Event", "Description"]]
            for event in recent_events:
                over_ball = f"{getattr(event, 'over_number', 0)}.{getattr(event, 'ball_number', 0)}"
                event_type = "WICKET" if getattr(event, 'is_wicket', False) else "RUNS"
                description = getattr(event, 'comment', '') or getattr(event, 'description', '')
                runs = getattr(event, 'runs', 0)
                
                # Add runs to description for run events
                if runs > 0 and not getattr(event, 'is_wicket', False):
                    description = f"{runs} runs" + (f" - {description}" if description else "")
                
                event_data.append([
                    str(getattr(event, 'over_number', 0)),
                    str(getattr(event, 'ball_number', 0)),
                    event_type,
                    description[:60] + "..." if len(description) > 60 else description
                ])
            
            events_table = Table(event_data, colWidths=[0.8*inch, 0.8*inch, 1*inch, 3.4*inch])
            events_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('FONTSIZE', (0, 1), (-1, -1), 8)
            ]))
            
            story.append(events_table)
        else:
            story.append(Paragraph("No events recorded", self.normal_style))
    
    def _add_batting_scorecard(self, story, team, title):
        """Add batting scorecard for a team"""
        story.append(Paragraph(f"{title}", self.header_style))
        story.append(Spacer(1, 10))
        
        players = getattr(team, 'players', [])
        if not players:
            story.append(Paragraph("No players data available", self.normal_style))
            story.append(Spacer(1, 15))
            return
        
        # Prepare batting data
        batting_data = [["Batsman", "Runs", "Balls", "4s", "6s", "S/R"]]
        
        for player in players:
            batting_stats = getattr(player, 'batting_stats', None)
            if batting_stats:
                batting_data.append([
                    getattr(player, 'name', 'Unknown'),
                    str(getattr(batting_stats, 'runs', 0)),
                    str(getattr(batting_stats, 'balls', 0)),
                    str(getattr(batting_stats, 'fours', 0)),
                    str(getattr(batting_stats, 'sixes', 0)),
                    f"{getattr(batting_stats, 'strike_rate', 0):.2f}" if getattr(batting_stats, 'strike_rate', 0) else "0.00"
                ])
        
        batting_table = Table(batting_data, colWidths=[2*inch, 0.8*inch, 0.8*inch, 0.5*inch, 0.5*inch, 0.8*inch])
        batting_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTSIZE', (0, 1), (-1, -1), 9)
        ]))
        
        story.append(batting_table)
        story.append(Spacer(1, 15))
    
    def _add_bowling_figures(self, story, team, title, match_data):
        """Add bowling figures for a team"""
        story.append(Paragraph(f"{title}", self.header_style))
        story.append(Spacer(1, 10))
        
        players = getattr(team, 'players', [])
        if not players:
            story.append(Paragraph("No bowling data available", self.normal_style))
            story.append(Spacer(1, 15))
            return
        
        # Debug bowling data and check alternative sources
        print(f"DEBUG PDF: Checking bowling figures for {title}")
        bowling_players_data = match_data.get('bowling_players', [])
        print(f"DEBUG PDF: bowling_players from match_data: {len(bowling_players_data)} players")
        
        for bp in bowling_players_data:
            print(f"  - {bp.get('name', 'Unknown')}: overs={bp.get('bowling_overs', 0)}, runs={bp.get('bowling_runs', 0)}, wickets={bp.get('bowling_wickets', 0)}")
        
        for player in players:
            bowling_stats = getattr(player, 'bowling_stats', None)
            if bowling_stats:
                balls = getattr(bowling_stats, 'balls', 0)
                runs = getattr(bowling_stats, 'runs', 0)
                wickets = getattr(bowling_stats, 'wickets', 0)
                economy = getattr(bowling_stats, 'economy', 0)
                print(f"  - {getattr(player, 'name', 'Unknown')}: balls={balls}, runs={runs}, wickets={wickets}")
        
        # Prepare bowling data (use bowling_players from match_data if available, fallback to player stats)
        bowling_data = [["Bowler", "Overs", "Runs", "Wickets", "Economy"]]
        
        # First try to use bowling_players from match_data
        if bowling_players_data:
            for bp in bowling_players_data:
                bowling_data.append([
                    bp.get('name', 'Unknown'),
                    f"{bp.get('bowling_overs', 0):.1f}",
                    str(bp.get('bowling_runs', 0)),
                    str(bp.get('bowling_wickets', 0)),
                    f"{bp.get('bowling_economy', 0):.2f}" if bp.get('bowling_economy', 0) > 0 else "0.00"
                ])
        else:
            # Fallback to player bowling_stats
            for player in players:
                bowling_stats = getattr(player, 'bowling_stats', None)
                if bowling_stats:
                    balls = getattr(bowling_stats, 'balls', 0)
                    runs = getattr(bowling_stats, 'runs', 0)
                    wickets = getattr(bowling_stats, 'wickets', 0)
                    economy = getattr(bowling_stats, 'economy', 0)
                    
                    bowling_data.append([
                        getattr(player, 'name', 'Unknown'),
                        f"{balls/6:.1f}" if balls > 0 else "0.0",
                        str(runs),
                        str(wickets),
                        f"{economy:.2f}" if economy > 0 else "0.00"
                    ])
        
        if len(bowling_data) == 1:  # Only header, no bowling data
            story.append(Paragraph("No bowling figures available", self.normal_style))
        else:
            bowling_table = Table(bowling_data, colWidths=[2*inch, 0.8*inch, 0.8*inch, 0.8*inch, 0.8*inch])
            bowling_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('FONTSIZE', (0, 1), (-1, -1), 9)
            ]))
            
            story.append(bowling_table)
        
        story.append(Spacer(1, 15))
    
    def _format_current_score(self, match_info):
        """Format current score string"""
        total_runs = getattr(match_info, 'total_runs', 0)
        wickets = getattr(match_info, 'wickets', 0)
        overs = getattr(match_info, 'current_over', 0)
        balls = getattr(match_info, 'current_ball', 0)
        
        return f"{total_runs}/{wickets} ({overs}.{balls} overs)"
    
    def prepare_match_data_for_pdf(self, match_data):
        """Convert match data to PDF-friendly format"""
        # This will be used to convert the match state to PDF-compatible format
        return {
            'match': match_data,
            'generated_at': datetime.now().isoformat()
        }


def generate_scoreboard_pdf(match_data, output_path=None):
    """Convenience function to generate PDF"""
    generator = CricketScoreboardPDF()
    return generator.generate_scoreboard_pdf(match_data, output_path)


if __name__ == "__main__":
    # Test the PDF generator
    from models import MatchState, Team, Player, PlayerRole, BattingStats, BowlingStats
    
    # Create sample data
    match = MatchState()
    match.team_a = Team("Team A")
    match.team_b = Team("Team B")
    match.total_runs = 156
    match.wickets = 4
    match.current_over = 18
    match.current_ball = 3
    match.max_overs = 20
    
    # Add sample players
    player1 = Player(id="1", name="Player 1", role=PlayerRole.BATSMAN)
    player1.batting_stats = BattingStats()
    player1.batting_stats.runs = 45
    player1.batting_stats.balls = 32
    player1.batting_stats.fours = 5
    player1.batting_stats.sixes = 2
    player1.batting_stats.update_strike_rate()
    
    player2 = Player(id="2", name="Player 2", role=PlayerRole.BOWLER)
    player2.bowling_stats = BowlingStats()
    player2.bowling_stats.overs = 3.5
    player2.bowling_stats.runs = 28
    player2.bowling_stats.wickets = 2
    player2.bowling_stats.update_economy()
    
    match.team_a.add_player(player1)
    match.team_a.add_player(player2)
    
    # Generate PDF
    match_data = {'match': match}
    pdf_path = generate_scoreboard_pdf(match_data)
    print(f"PDF generated: {pdf_path}")
