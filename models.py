"""
Core data models for Cricket Scoring Application
Contains Player, Team, MatchState classes and related enums
"""

from enum import Enum
from typing import List, Optional, Dict, Any
from dataclasses import dataclass, field
import json


class PlayerRole(Enum):
    BATSMAN = "batsman"
    BOWLER = "bowler"
    ALL_ROUNDER = "all-rounder"
    WICKET_KEEPER = "wicket-keeper"


class WicketType(Enum):
    BOWLED = "Bowled"
    CAUGHT = "Caught"
    LBW = "LBW"
    RUN_OUT = "Run Out"
    STUMPED = "Stumped"
    HIT_WICKET = "Hit Wicket"
    RETIRED = "Retired"


@dataclass
class BattingStats:
    runs: int = 0
    balls: int = 0
    fours: int = 0
    sixes: int = 0
    strike_rate: float = 0.0
    
    def update_strike_rate(self):
        if self.balls > 0:
            self.strike_rate = round((self.runs / self.balls) * 100, 2)


@dataclass
class BowlingStats:
    overs: float = 0.0
    runs: int = 0
    wickets: int = 0
    economy: float = 0.0
    wides: int = 0
    no_balls: int = 0
    
    def update_economy(self):
        if self.overs > 0:
            self.economy = round(self.runs / self.overs, 2)
    
    def get_average(self) -> float:
        if self.wickets > 0:
            return round(self.runs / self.wickets, 2)
        return 0.0


@dataclass
class Player:
    id: str
    name: str
    role: PlayerRole = PlayerRole.BATSMAN
    batting_stats: BattingStats = field(default_factory=BattingStats)
    bowling_stats: BowlingStats = field(default_factory=BowlingStats)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'name': self.name,
            'role': self.role.value,
            'batting_stats': {
                'runs': self.batting_stats.runs,
                'balls': self.batting_stats.balls,
                'fours': self.batting_stats.fours,
                'sixes': self.batting_stats.sixes,
                'strike_rate': self.batting_stats.strike_rate
            },
            'bowling_stats': {
                'overs': self.bowling_stats.overs,
                'runs': self.bowling_stats.runs,
                'wickets': self.bowling_stats.wickets,
                'economy': self.bowling_stats.economy,
                'wides': self.bowling_stats.wides,
                'no_balls': self.bowling_stats.no_balls,
                'average': self.bowling_stats.get_average()
            }
        }


@dataclass
class Team:
    team_name: str
    players: List[Player] = field(default_factory=list)
    batting_order: List[str] = field(default_factory=list)  # Player IDs who batted
    bowling_order: List[str] = field(default_factory=list)  # Player IDs who bowled
    captain_id: Optional[str] = None  # Player ID of captain
    
    def add_player(self, player: Player):
        """Add a new player to the team"""
        if player.id not in [p.id for p in self.players]:
            self.players.append(player)
    
    def get_player_by_id(self, player_id: str) -> Optional[Player]:
        """Get player by ID"""
        for player in self.players:
            if player.id == player_id:
                return player
        return None
    
    def get_players_not_batted(self) -> List[Player]:
        """Get players who haven't batted yet"""
        batted_ids = set(self.batting_order)
        return [p for p in self.players if p.id not in batted_ids]
    
    def get_bowlers(self) -> List[Player]:
        """Get all players who can bowl"""
        return [p for p in self.players if p.role in [PlayerRole.BOWLER, PlayerRole.ALL_ROUNDER]]
    
    def get_top_batsmen(self, limit: int = 5) -> List[Player]:
        """Get top batsmen by runs scored"""
        return sorted(self.players, key=lambda p: p.batting_stats.runs, reverse=True)[:limit]
    
    def get_top_bowlers(self, limit: int = 5) -> List[Player]:
        """Get top bowlers by wickets taken"""
        return sorted(self.players, key=lambda p: p.bowling_stats.wickets, reverse=True)[:limit]
    
    def get_captain(self) -> Optional[Player]:
        """Get the captain of the team"""
        if self.captain_id:
            return self.get_player_by_id(self.captain_id)
        return None
    
    def set_captain(self, player_id: str):
        """Set the captain of the team"""
        if self.get_player_by_id(player_id):
            self.captain_id = player_id
        else:
            raise ValueError("Player not found in team")


@dataclass
class BallEvent:
    ball_number: int
    over_number: int
    runs: int
    is_wicket: bool = False
    wicket_type: Optional[WicketType] = None
    batsman_id: Optional[str] = None
    bowler_id: Optional[str] = None
    catcher_id: Optional[str] = None
    runout_by: Optional[List[str]] = None
    extra_type: Optional[str] = None  # wide, no-ball, bye, leg-bye, dead-ball
    description: str = ""
    comment: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'over': self.over_number,
            'ball': self.ball_number,
            'runs': self.runs,
            'batsman': self.batsman_id,
            'bowler': self.bowler_id,
            'description': self.description,
            'comment': self.comment
        }


@dataclass
class MatchState:
    team_a: Optional[Team] = None
    team_b: Optional[Team] = None
    current_innings: int = 1  # 1 or 2
    batting_team: Optional[Team] = None
    bowling_team: Optional[Team] = None
    max_overs: Optional[int] = None
    batting_first_team_name: Optional[str] = None
    match_name: Optional[str] = None  # Custom match name or auto-generated
    
    # First innings summary for target calculation
    first_innings_summary: Optional[Dict[str, Any]] = None
    
    # Current players
    striker: Optional[Player] = None
    non_striker: Optional[Player] = None
    current_bowler: Optional[Player] = None
    
    # Match status
    current_over: int = 0
    current_ball: int = 0
    total_runs: int = 0
    wickets: int = 0
    overs_completed: float = 0.0
    
    # Events history for undo functionality
    events: List[BallEvent] = field(default_factory=list)
    
    def add_event(self, event: BallEvent):
        """Add a ball event to history"""
        self.events.append(event)
    
    def undo_last_event(self) -> Optional[BallEvent]:
        """Remove and return the last event"""
        if self.events:
            return self.events.pop()
        return None
    
    def get_match_summary(self) -> Dict[str, Any]:
        """Get current match summary"""
        return {
            'innings': self.current_innings,
            'batting_team': self.batting_team.team_name if self.batting_team else None,
            'bowling_team': self.bowling_team.team_name if self.bowling_team else None,
            'runs': self.total_runs,
            'wickets': self.wickets,
            'overs': f"{self.current_over}.{self.current_ball}",
            'max_overs': self.max_overs,
            'striker': self.striker.name if self.striker else None,
            'non_striker': self.non_striker.name if self.non_striker else None,
            'bowler': self.current_bowler.name if self.current_bowler else None
        }

    def get_innings_summary(self) -> Dict[str, Any]:
        """Get summary for completed innings"""
        # Calculate extras
        wides = 0
        no_balls = 0
        byes = 0
        leg_byes = 0
        
        for event in self.events:
            if event.extra_type == "wide":
                wides += 1
            elif event.extra_type == "no-ball":
                no_balls += 1
            elif event.extra_type == "bye":
                byes += event.runs
            elif event.extra_type == "leg-bye":
                leg_byes += event.runs
        
        extras = wides + no_balls + byes + leg_byes
        
        return {
            'team': self.batting_team.team_name if self.batting_team else None,
            'runs': self.total_runs,
            'wickets': self.wickets,
            'overs': f"{self.current_over}.{self.current_ball}",
            'max_overs': self.max_overs,
            'extras': {
                'total': extras,
                'wides': wides,
                'no_balls': no_balls,
                'byes': byes,
                'leg_byes': leg_byes
            }
        }

    def is_innings_complete(self) -> bool:
        """Check if innings is complete (all overs bowled, all wickets fallen, or target achieved)"""
        if self.max_overs is None:
            return False
        
        # Check if all overs bowled
        overs_complete = self.current_over >= self.max_overs and self.current_ball == 0
        
        # Check if all wickets fallen
        all_out = self.batting_team and len(self.batting_team.batting_order) >= len(self.batting_team.players) and self.wickets >= len(self.batting_team.players) - 1
        
        # Check if target achieved (second innings only)
        target_achieved = False
        if self.current_innings == 2 and self.first_innings_summary:
            target = self.first_innings_summary["runs"] + 1
            target_achieved = self.total_runs >= target
        
        return overs_complete or all_out or target_achieved

    def is_match_complete(self) -> bool:
        """Check if the entire match is complete"""
        if not self.first_innings_summary or self.current_innings != 2:
            return False
        
        # Check if second innings is complete
        return self.is_innings_complete()

    def get_match_winner(self) -> Optional[str]:
        """Get the winning team"""
        if not self.is_match_complete():
            return None
        
        if self.current_innings == 2 and self.first_innings_summary:
            target = self.first_innings_summary["runs"] + 1
            if self.total_runs >= target:
                # Second innings team achieved target
                return self.batting_team.team_name if self.batting_team else None
            else:
                # First innings team won (second innings failed to achieve target)
                return self.bowling_team.team_name if self.bowling_team else None
        
        return None

    def get_player_dismissal(self, player_id: str) -> Optional[Dict[str, Any]]:
        """Get dismissal details for a player"""
        for event in self.events:
            if event.batsman_id == player_id and event.is_wicket:
                dismissal = {
                    'type': event.wicket_type.value.replace('_', ' ').title(),
                    'bowler': None,
                    'catcher': None,
                    'runout_by': []
                }
                
                # Find bowler name
                if event.bowler_id:
                    for team in [self.team_a, self.team_b]:
                        if team:
                            for player in team.players:
                                if player.id == event.bowler_id:
                                    dismissal['bowler'] = player.name
                                    break
                
                # Find catcher name
                if event.catcher_id:
                    for team in [self.team_a, self.team_b]:
                        if team:
                            for player in team.players:
                                if player.id == event.catcher_id:
                                    dismissal['catcher'] = player.name
                                    break
                
                # Find runout players
                if event.runout_by:
                    for team in [self.team_a, self.team_b]:
                        if team:
                            for player in team.players:
                                if player.id in event.runout_by:
                                    dismissal['runout_by'].append(player.name)
                
                return dismissal
        return None

    def switch_innings(self):
        """Switch batting and bowling teams for next innings"""
        # Store first innings summary
        if self.current_innings == 1:
            self.first_innings_summary = self.get_innings_summary()
        
        self.batting_team, self.bowling_team = self.bowling_team, self.batting_team
        self.current_innings += 1
        self.current_over = 0
        self.current_ball = 0
        self.total_runs = 0
        self.wickets = 0
        self.striker = None
        self.non_striker = None
        self.current_bowler = None
        self.events.clear()

    def get_match_result(self) -> Dict[str, Any]:
        """Get match result with winner and player of the match"""
        if not self.first_innings_summary or self.current_innings != 2:
            return None
        
        first_runs = self.first_innings_summary["runs"]
        second_runs = self.total_runs
        
        # Determine winner
        if second_runs > first_runs:
            winner = self.batting_team.team_name
            margin = f"{len(self.batting_team.players) - self.wickets} wickets"
        elif second_runs < first_runs:
            winner = self.bowling_team.team_name
            margin = f"{first_runs - second_runs} runs"
        else:
            winner = "Draw"
            margin = "Tie"
        
        # Calculate player of match
        all_players = []
        
        # Add batting stats
        for team in [self.team_a, self.team_b]:
            if team:
                for player in team.players:
                    batting_score = player.batting_stats.runs
                    bowling_score = player.bowling_stats.wickets * 20 + player.bowling_stats.runs // 10
                    total_score = batting_score + bowling_score
                    all_players.append({
                        'name': player.name,
                        'team': team.team_name,
                        'batting_runs': player.batting_stats.runs,
                        'batting_balls': player.batting_stats.balls,
                        'bowling_wickets': player.bowling_stats.wickets,
                        'bowling_runs': player.bowling_stats.runs,
                        'total_score': total_score
                    })
        
        # Sort by total score and get top performer
        player_of_match = max(all_players, key=lambda x: x['total_score']) if all_players else None
        
        return {
            'winner': winner,
            'margin': margin,
            'first_innings': self.first_innings_summary,
            'second_innings': self.get_innings_summary(),
            'player_of_match': player_of_match,
            'all_players': sorted(all_players, key=lambda x: x['total_score'], reverse=True)
        }

    def get_ball_by_ball(self) -> List[Dict[str, Any]]:
        """Get list of all balls with details"""
        return [event.to_dict() for event in self.events]


# Import UUID for unique player IDs
import uuid
