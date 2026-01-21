"""
Main Cricket Scoring Application
Built with Python + Tkinter for dynamic player management and live scoring
"""

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from models import *


class CricketScorerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Cricket Scorer - Local Friendly Matches")
        self.root.geometry("1200x700")
        
        # Initialize match state
        self.match_state = MatchState()
        
        # Setup UI
        self.setup_ui()
        self.show_team_setup()
    
    def setup_ui(self):
        # Main container
        self.main_frame = ttk.Frame(self.root, padding="10")
        self.main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        self.main_frame.columnconfigure(0, weight=1)
        self.main_frame.rowconfigure(0, weight=1)
    
    def clear_main_frame(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()
    
    def show_team_setup(self):
        self.clear_main_frame()
        
        # Team Setup Frame
        setup_frame = ttk.LabelFrame(self.main_frame, text="Match Setup", padding="20")
        setup_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Team A Setup
        ttk.Label(setup_frame, text="Team A:", font=("Arial", 12, "bold")).grid(row=0, column=0, columnspan=2, pady=10)
        
        ttk.Label(setup_frame, text="Team Name:").grid(row=1, column=0, sticky=tk.W)
        self.team_a_name = ttk.Entry(setup_frame, width=30)
        self.team_a_name.grid(row=1, column=1, padx=5)
        
        ttk.Button(setup_frame, text="Add Players", command=lambda: self.add_players_dialog('A')).grid(row=2, column=0, columnspan=2, pady=5)
        
        # Team B Setup
        ttk.Label(setup_frame, text="Team B:", font=("Arial", 12, "bold")).grid(row=3, column=0, columnspan=2, pady=(20, 10))
        
        ttk.Label(setup_frame, text="Team Name:").grid(row=4, column=0, sticky=tk.W)
        self.team_b_name = ttk.Entry(setup_frame, width=30)
        self.team_b_name.grid(row=4, column=1, padx=5)
        
        ttk.Button(setup_frame, text="Add Players", command=lambda: self.add_players_dialog('B')).grid(row=5, column=0, columnspan=2, pady=5)

        ttk.Separator(setup_frame, orient='horizontal').grid(row=6, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=15)

        ttk.Label(setup_frame, text="Overs:").grid(row=7, column=0, sticky=tk.W)
        self.overs_var = tk.StringVar(value="5")
        self.overs_entry = ttk.Entry(setup_frame, width=10, textvariable=self.overs_var)
        self.overs_entry.grid(row=7, column=1, sticky=tk.W, padx=5)

        ttk.Label(setup_frame, text="Batting First:").grid(row=8, column=0, sticky=tk.W)
        self.batting_first_var = tk.StringVar(value="")
        self.batting_first_combo = ttk.Combobox(setup_frame, textvariable=self.batting_first_var, state="readonly", width=27)
        self.batting_first_combo['values'] = ["Team A", "Team B"]
        self.batting_first_combo.grid(row=8, column=1, sticky=tk.W, padx=5)

        # Start Match Button
        ttk.Button(setup_frame, text="Start Match", command=self.start_match).grid(row=9, column=0, columnspan=2, pady=20)
    
    def add_players_dialog(self, team_letter):
        dialog = tk.Toplevel(self.root)
        dialog.title(f"Add Players - Team {team_letter}")
        dialog.geometry("400x500")
        
        players_list = []
        
        # Player entry
        entry_frame = ttk.Frame(dialog)
        entry_frame.pack(pady=10)
        
        ttk.Label(entry_frame, text="Player Name:").pack(side=tk.LEFT)
        name_entry = ttk.Entry(entry_frame, width=30)
        name_entry.pack(side=tk.LEFT, padx=5)
        
        role_var = tk.StringVar(value="Unknown")
        role_combo = ttk.Combobox(entry_frame, textvariable=role_var, 
                                  values=["Batsman", "Bowler", "All-rounder", "Unknown"], 
                                  width=15, state="readonly")
        role_combo.pack(side=tk.LEFT, padx=5)
        
        def add_player():
            name = name_entry.get().strip()
            if name:
                role_map = {
                    "Batsman": PlayerRole.BATSMAN,
                    "Bowler": PlayerRole.BOWLER,
                    "All-rounder": PlayerRole.ALL_ROUNDER,
                    "Unknown": PlayerRole.UNKNOWN
                }
                player = Player(
                    id=str(uuid.uuid4()),
                    name=name,
                    role=role_map.get(role_var.get(), PlayerRole.UNKNOWN)
                )
                players_list.append(player)
                player_listbox.insert(tk.END, f"{name} ({role_var.get()})")
                name_entry.delete(0, tk.END)
        
        ttk.Button(entry_frame, text="Add Player", command=add_player).pack(side=tk.LEFT, padx=5)
        
        # Players list
        list_frame = ttk.Frame(dialog)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        scrollbar = ttk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        player_listbox = tk.Listbox(list_frame, yscrollcommand=scrollbar.set)
        player_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=player_listbox.yview)
        
        def save_players():
            if team_letter == 'A':
                self.match_state.team_a = Team(self.team_a_name.get() or "Team A", players_list)
            else:
                self.match_state.team_b = Team(self.team_b_name.get() or "Team B", players_list)
            dialog.destroy()
        
        # Buttons
        button_frame = ttk.Frame(dialog)
        button_frame.pack(pady=10)
        
        ttk.Button(button_frame, text="Save", command=save_players).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=dialog.destroy).pack(side=tk.LEFT, padx=5)
    
    def start_match(self):
        if not self.match_state.team_a or not self.match_state.team_b:
            messagebox.showwarning("Warning", "Please set up both teams first!")
            return

        team_a_name = (self.team_a_name.get() if hasattr(self, 'team_a_name') else "").strip() or "Team A"
        team_b_name = (self.team_b_name.get() if hasattr(self, 'team_b_name') else "").strip() or "Team B"
        self.match_state.team_a.team_name = team_a_name
        self.match_state.team_b.team_name = team_b_name
        if hasattr(self, 'batting_first_combo'):
            self.batting_first_combo['values'] = [team_a_name, team_b_name]

        if len(self.match_state.team_a.players) < 2 or len(self.match_state.team_b.players) < 2:
            messagebox.showwarning("Warning", "Each team must have at least 2 players before starting the match.")
            return

        overs_text = (self.overs_var.get() if hasattr(self, 'overs_var') else "").strip()
        try:
            overs = int(overs_text)
        except ValueError:
            overs = 0
        if overs <= 0:
            messagebox.showwarning("Warning", "Please enter a valid number of overs (e.g. 5, 10).")
            return

        batting_first = (self.batting_first_var.get() if hasattr(self, 'batting_first_var') else "").strip()
        if batting_first not in [team_a_name, team_b_name]:
            messagebox.showwarning("Warning", "Please select which team is batting first.")
            return

        self.match_state.max_overs = overs
        self.match_state.batting_first_team_name = batting_first

        if batting_first == team_a_name:
            self.match_state.batting_team = self.match_state.team_a
            self.match_state.bowling_team = self.match_state.team_b
        else:
            self.match_state.batting_team = self.match_state.team_b
            self.match_state.bowling_team = self.match_state.team_a

        self.show_scoring_interface()
        self.select_openers()
    
    def show_scoring_interface(self):
        self.clear_main_frame()
        
        # Main scoring frame
        scoring_frame = ttk.Frame(self.main_frame)
        scoring_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Score display
        score_frame = ttk.LabelFrame(scoring_frame, text="Score", padding="10")
        score_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        self.score_label = ttk.Label(score_frame, text="", font=("Arial", 16, "bold"))
        self.score_label.pack()
        
        # Current players display
        players_frame = ttk.LabelFrame(scoring_frame, text="Current Players", padding="10")
        players_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        self.players_label = ttk.Label(players_frame, text="", font=("Arial", 12))
        self.players_label.pack()
        
        # Scoring buttons
        buttons_frame = ttk.LabelFrame(scoring_frame, text="Scoring", padding="10")
        buttons_frame.grid(row=2, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        
        # Run buttons
        runs_frame = ttk.Frame(buttons_frame)
        runs_frame.pack(pady=5)
        
        for runs in [0, 1, 2, 3, 4, 6]:
            ttk.Button(runs_frame, text=str(runs), width=5, 
                      command=lambda r=runs: self.score_runs(r)).pack(side=tk.LEFT, padx=2)
        
        # Wicket button
        ttk.Button(buttons_frame, text="Wicket", command=self.wicket_fallen).pack(pady=5)
        
        # Extras
        extras_frame = ttk.Frame(buttons_frame)
        extras_frame.pack(pady=5)
        
        ttk.Button(extras_frame, text="Wide", command=lambda: self.add_extra("wide")).pack(side=tk.LEFT, padx=2)
        ttk.Button(extras_frame, text="No Ball", command=lambda: self.add_extra("no-ball")).pack(side=tk.LEFT, padx=2)
        ttk.Button(extras_frame, text="Bye", command=lambda: self.add_extra("bye")).pack(side=tk.LEFT, padx=2)
        ttk.Button(extras_frame, text="Leg Bye", command=lambda: self.add_extra("leg-bye")).pack(side=tk.LEFT, padx=2)
        
        # Control buttons
        control_frame = ttk.LabelFrame(scoring_frame, text="Controls", padding="10")
        control_frame.grid(row=2, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5, padx=5)
        
        ttk.Button(control_frame, text="Undo", command=self.undo_last_ball).pack(pady=2)
        ttk.Button(control_frame, text="Change Strike", command=self.change_strike).pack(pady=2)
        ttk.Button(control_frame, text="Change Bowler", command=self.change_bowler).pack(pady=2)
        ttk.Button(control_frame, text="Add Player", command=self.add_player_during_match).pack(pady=2)
        
        self.update_display()
    
    def select_openers(self):
        if not self.match_state.batting_team.players:
            # Add players on the fly
            self.add_player_on_fly("batsman", self.set_striker)
            return
        
        dialog = tk.Toplevel(self.root)
        dialog.title("Select Opening Batsmen")
        dialog.geometry("400x300")
        
        ttk.Label(dialog, text="Select Striker:", font=("Arial", 10, "bold")).pack(pady=5)
        
        striker_var = tk.StringVar()
        striker_combo = ttk.Combobox(dialog, textvariable=striker_var, state="readonly")
        striker_combo['values'] = [p.name for p in self.match_state.batting_team.players]
        striker_combo.pack(pady=5)
        
        ttk.Label(dialog, text="Select Non-Striker:", font=("Arial", 10, "bold")).pack(pady=5)
        
        non_striker_var = tk.StringVar()
        non_striker_combo = ttk.Combobox(dialog, textvariable=non_striker_var, state="readonly")
        non_striker_combo['values'] = [p.name for p in self.match_state.batting_team.players]
        non_striker_combo.pack(pady=5)
        
        def add_new_batsman():
            self.add_player_on_fly("batsman", lambda: None)
        
        ttk.Button(dialog, text="Add New Player", command=add_new_batsman).pack(pady=10)
        
        def confirm_openers():
            striker_name = striker_var.get()
            non_striker_name = non_striker_var.get()
            
            if striker_name and non_striker_name and striker_name != non_striker_name:
                self.match_state.striker = next(p for p in self.match_state.batting_team.players if p.name == striker_name)
                self.match_state.non_striker = next(p for p in self.match_state.batting_team.players if p.name == non_striker_name)
                
                self.match_state.batting_team.batting_order.extend([self.match_state.striker.id, self.match_state.non_striker.id])
                dialog.destroy()
                self.select_first_bowler()
            else:
                messagebox.showwarning("Warning", "Please select two different players!")
        
        ttk.Button(dialog, text="Confirm", command=confirm_openers).pack(pady=10)
    
    def select_first_bowler(self):
        if not self.match_state.bowling_team.players:
            self.add_player_on_fly("bowler", self.set_bowler)
            return
        
        dialog = tk.Toplevel(self.root)
        dialog.title("Select First Bowler")
        dialog.geometry("300x200")
        
        ttk.Label(dialog, text="Select Bowler:", font=("Arial", 10, "bold")).pack(pady=10)
        
        bowler_var = tk.StringVar()
        bowler_combo = ttk.Combobox(dialog, textvariable=bowler_var, state="readonly")
        bowler_combo['values'] = [p.name for p in self.match_state.bowling_team.get_bowlers()]
        bowler_combo.pack(pady=10)
        
        def add_new_bowler():
            self.add_player_on_fly("bowler", lambda: None)
        
        ttk.Button(dialog, text="Add New Player", command=add_new_bowler).pack(pady=5)
        
        def confirm_bowler():
            bowler_name = bowler_var.get()
            if bowler_name:
                self.match_state.current_bowler = next(p for p in self.match_state.bowling_team.players if p.name == bowler_name)
                self.match_state.bowling_team.bowling_order.append(self.match_state.current_bowler.id)
                dialog.destroy()
                self.update_display()
        
        ttk.Button(dialog, text="Confirm", command=confirm_bowler).pack(pady=10)
    
    def update_display(self):
        if hasattr(self, 'score_label'):
            summary = self.match_state.get_match_summary()
            score_text = f"{summary['batting_team']}: {summary['runs']}/{summary['wickets']} ({summary['overs']} overs)"
            self.score_label.config(text=score_text)
            
            players_text = f"Striker: {summary['striker'] or 'Not set'} | Non-Striker: {summary['non_striker'] or 'Not set'} | Bowler: {summary['bowler'] or 'Not set'}"
            self.players_label.config(text=players_text)
    
    def score_runs(self, runs):
        if not self.match_state.striker or not self.match_state.current_bowler:
            messagebox.showwarning("Warning", "Please set up players first!")
            return
        
        # Update striker stats
        self.match_state.striker.batting_stats.runs += runs
        self.match_state.striker.batting_stats.balls += 1
        self.match_state.striker.batting_stats.update_strike_rate()
        
        # Update bowler stats
        self.match_state.current_bowler.bowling_stats.runs += runs
        self.match_state.current_bowler.bowling_stats.overs += 1/6
        self.match_state.current_bowler.bowling_stats.update_economy()
        
        # Update match totals
        self.match_state.total_runs += runs
        
        # Handle strike rotation for odd runs
        if runs % 2 == 1:
            self.match_state.striker, self.match_state.non_striker = self.match_state.non_striker, self.match_state.striker
        
        # Update ball count
        self.match_state.current_ball += 1
        if self.match_state.current_ball >= 6:
            self.match_state.current_ball = 0
            self.match_state.current_over += 1
            self.select_new_bowler()
        
        # Create event
        event = BallEvent(
            ball_number=self.match_state.current_ball,
            over_number=self.match_state.current_over,
            runs=runs,
            batsman_id=self.match_state.striker.id,
            bowler_id=self.match_state.current_bowler.id,
            description=f"{runs} runs"
        )
        self.match_state.add_event(event)
        
        self.update_display()
    
    def wicket_fallen(self):
        if not self.match_state.striker:
            messagebox.showwarning("Warning", "No striker set!")
            return
        
        # Update wicket count
        self.match_state.wickets += 1
        
        # Update bowler stats
        self.match_state.current_bowler.bowling_stats.wickets += 1
        
        # Update striker stats
        self.match_state.striker.batting_stats.balls += 1
        self.match_state.striker.batting_stats.update_strike_rate()
        
        # Select next batsman
        self.select_next_batsman()
    
    def select_next_batsman(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("Select Next Batsman")
        dialog.geometry("400x300")
        
        ttk.Label(dialog, text="Select Next Batsman:", font=("Arial", 10, "bold")).pack(pady=10)
        
        available_players = self.match_state.batting_team.get_players_not_batted()
        player_names = [p.name for p in available_players]
        
        if player_names:
            batsman_var = tk.StringVar()
            batsman_combo = ttk.Combobox(dialog, textvariable=batsman_var, state="readonly")
            batsman_combo['values'] = player_names
            batsman_combo.pack(pady=10)
        
        def add_new_batsman():
            self.add_player_on_fly("batsman", lambda: None)
        
        ttk.Button(dialog, text="Add New Player", command=add_new_batsman).pack(pady=10)
        
        def confirm_batsman():
            if player_names:
                batsman_name = batsman_var.get()
                if batsman_name:
                    new_batsman = next(p for p in available_players if p.name == batsman_name)
                    self.match_state.striker = new_batsman
                    self.match_state.batting_team.batting_order.append(new_batsman.id)
                    dialog.destroy()
                    self.update_display()
        
        ttk.Button(dialog, text="Confirm", command=confirm_batsman).pack(pady=10)
    
    def select_new_bowler(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("Select New Bowler")
        dialog.geometry("300x200")
        
        ttk.Label(dialog, text="Select Bowler:", font=("Arial", 10, "bold")).pack(pady=10)
        
        bowler_var = tk.StringVar()
        bowler_combo = ttk.Combobox(dialog, textvariable=bowler_var, state="readonly")
        bowler_combo['values'] = [p.name for p in self.match_state.bowling_team.get_bowlers()]
        bowler_combo.pack(pady=10)
        
        def add_new_bowler():
            self.add_player_on_fly("bowler", lambda: None)
        
        ttk.Button(dialog, text="Add New Player", command=add_new_bowler).pack(pady=5)
        
        def confirm_bowler():
            bowler_name = bowler_var.get()
            if bowler_name:
                self.match_state.current_bowler = next(p for p in self.match_state.bowling_team.players if p.name == bowler_name)
                self.match_state.bowling_team.bowling_order.append(self.match_state.current_bowler.id)
                dialog.destroy()
                self.update_display()
        
        ttk.Button(dialog, text="Confirm", command=confirm_bowler).pack(pady=10)
    
    def add_player_on_fly(self, player_type, callback):
        dialog = tk.Toplevel(self.root)
        dialog.title(f"Add New {player_type.title()}")
        dialog.geometry("300x200")
        
        ttk.Label(dialog, text="Player Name:").pack(pady=10)
        name_entry = ttk.Entry(dialog, width=30)
        name_entry.pack(pady=5)
        
        role_var = tk.StringVar(value=player_type)
        
        def add_player():
            name = name_entry.get().strip()
            if name:
                role_map = {
                    "Batsman": PlayerRole.BATSMAN,
                    "Bowler": PlayerRole.BOWLER,
                    "All-rounder": PlayerRole.ALL_ROUNDER,
                    "Unknown": PlayerRole.UNKNOWN
                }
                player = Player(
                    id=str(uuid.uuid4()),
                    name=name,
                    role=role_map.get(role_var.get(), PlayerRole.UNKNOWN)
                )
                
                if self.match_state.batting_team and player_type == "batsman":
                    self.match_state.batting_team.add_player(player)
                elif self.match_state.bowling_team and player_type == "bowler":
                    self.match_state.bowling_team.add_player(player)
                
                dialog.destroy()
                callback()
        
        ttk.Button(dialog, text="Add Player", command=add_player).pack(pady=10)
    
    def add_extra(self, extra_type):
        if extra_type in ["wide", "no-ball"]:
            self.match_state.total_runs += 1
            self.match_state.current_bowler.bowling_stats.runs += 1
        else:
            self.match_state.total_runs += 1
        
        self.update_display()
    
    def change_strike(self):
        if self.match_state.striker and self.match_state.non_striker:
            self.match_state.striker, self.match_state.non_striker = self.match_state.non_striker, self.match_state.striker
            self.update_display()
    
    def change_bowler(self):
        self.select_new_bowler()
    
    def add_player_during_match(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("Add Player During Match")
        dialog.geometry("300x250")
        
        ttk.Label(dialog, text="Player Name:").pack(pady=10)
        name_entry = ttk.Entry(dialog, width=30)
        name_entry.pack(pady=5)
        
        ttk.Label(dialog, text="Role:").pack(pady=5)
        role_var = tk.StringVar(value="Unknown")
        role_combo = ttk.Combobox(dialog, textvariable=role_var, 
                                  values=["Batsman", "Bowler", "All-rounder", "Unknown"], 
                                  width=20, state="readonly")
        role_combo.pack(pady=5)
        
        ttk.Label(dialog, text="Add to Team:").pack(pady=5)
        team_var = tk.StringVar(value="batting")
        team_combo = ttk.Combobox(dialog, textvariable=team_var, 
                                  values=["batting", "bowling"], 
                                  width=20, state="readonly")
        team_combo.pack(pady=5)
        
        def add_player():
            name = name_entry.get().strip()
            if name:
                role_map = {
                    "Batsman": PlayerRole.BATSMAN,
                    "Bowler": PlayerRole.BOWLER,
                    "All-rounder": PlayerRole.ALL_ROUNDER,
                    "Unknown": PlayerRole.UNKNOWN
                }
                player = Player(
                    id=str(uuid.uuid4()),
                    name=name,
                    role=role_map.get(role_var.get(), PlayerRole.UNKNOWN)
                )
                
                if team_var.get() == "batting":
                    self.match_state.batting_team.add_player(player)
                else:
                    self.match_state.bowling_team.add_player(player)
                
                dialog.destroy()
                self.update_display()
        
        ttk.Button(dialog, text="Add Player", command=add_player).pack(pady=10)
    
    def undo_last_ball(self):
        event = self.match_state.undo_last_event()
        if event:
            messagebox.showinfo("Undo", f"Undid: {event.description}")
            self.update_display()
        else:
            messagebox.showinfo("Undo", "No events to undo")
    
    def set_striker(self):
        pass
    
    def set_bowler(self):
        pass


if __name__ == "__main__":
    root = tk.Tk()
    app = CricketScorerApp(root)
    root.mainloop()
