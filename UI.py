from tkinter import *
from autocomplete_entry import Combobox_Autocomplete
from skills_db import SkillsDB
from tkinter import font
from Utils import Utils

class UI:
    def __init__(self):
        self.skills_file_path = "skills.csv"
        self.actions_file_path = "actions.csv"
        self.domains_file_path = "domains.csv"
        self.domains_distance_file_path = "domains_distance_matrix.csv"
        self.sdb_on_debug = False
        self.debug = None

        self.sdb = SkillsDB(self.skills_file_path, domains_distance_matrix_path=self.domains_distance_file_path)

        self.initialize_window(self.sdb.skills_names)

    def validate_skill_names(self, skill1_name, skill2_name):
        valid_names = True
        if skill1_name == "" or skill2_name == "":
            self.result_label["text"] = "Man Please Enter Both Skills"
            valid_names = False

        elif skill1_name not in self.sdb.skills_names:
            self.result_label["text"] = "First Skill is not in the Data Base"
            valid_names = False

        elif skill2_name not in self.sdb.skills_names:
            self.result_label["text"] = "Second Skill is not in the Data Base"
            valid_names = False

        return valid_names

    def calc_distance(self):
        debug = self.debug.get()
        skill1_name = self.skill_selector1.get()
        skill2_name = self.skill_selector2.get()

        if not self.validate_skill_names(skill1_name,skill2_name):
            return

        if debug and not self.sdb_on_debug:
            self.sdb = SkillsDB(self.skills_file_path, actions_file_path=self.actions_file_path,
                                domains_file_path=self.domains_file_path)
            self.sdb_on_debug = True

        distance, debug_info = self.sdb.calc_skills_distance(skill1_name, skill2_name, debug)
        self.result_label["text"] = distance

        if debug:
            Utils.write_str_to_file(debug_info,"debug-info.txt")



    def initialize_window(self , skills_name):
        root = Tk()
        root.title("SupportFinity AI Debugger")
        root.geometry("600x250")
        root.configure(background="#F6F6F6")
        self.debug = BooleanVar()

        # configuration
        button_font = font.Font(family='Helvetica', size=9, weight='bold')
        WINDOW_BACKGROUND = "#F6F6F6"
        SECOND_COLOR = "#C70000"
        TEXTBOX_SEPARATION = 10
        TEXTBOX_WIDTH = 40

        main_frame = Frame(root , background=WINDOW_BACKGROUND)
        main_frame.pack(padx=20, pady=30)

        skill_label1 = Label(main_frame , background = WINDOW_BACKGROUND , text="First Skill")
        skill_label1.grid(row=0, sticky=W , padx = (0, TEXTBOX_SEPARATION))

        skill_label2 = Label(main_frame , background = WINDOW_BACKGROUND , text="Second Skill")
        skill_label2.grid(row=0 , column = 1 , sticky=W , padx = (TEXTBOX_SEPARATION , 0))

        options = skills_name

        self.skill_selector1 = Combobox_Autocomplete(main_frame,options,highlightthickness=1, width =TEXTBOX_WIDTH)
        self.skill_selector1.grid(row=1, padx=(0, TEXTBOX_SEPARATION), sticky=W)
        # skill_selector1["Font"] = button_font

        self.skill_selector2 = Combobox_Autocomplete(main_frame,options,highlightthickness=1, width =TEXTBOX_WIDTH)
        self.skill_selector2.grid(row=1, column=1, padx=(TEXTBOX_SEPARATION, 0), sticky=E)

        debug_checkbox = Checkbutton(main_frame , text="Debug" ,variable=self.debug, background=WINDOW_BACKGROUND)
        debug_checkbox.grid(row=2, sticky=W, pady=(10,0))
        calc_distance_button = Button(main_frame, text="Test Connectivity", command=self.calc_distance, background=SECOND_COLOR, fg="#FFFFFF")
        calc_distance_button.grid(row = 3 , columnspan=2 , sticky=W + E ,pady=(20,20) , padx="60")
        calc_distance_button["font"] = button_font

        self.result_label = Label(main_frame , text="no man", background=WINDOW_BACKGROUND)
        self.result_label.grid(row = 4 , columnspan=2)
        self.result_label['text'] = "...."

        root.mainloop()



UI()