from config       import *
from utils        import *



class Debug():
    def __init__(self, master):
        self.master = master
        self.mk_tkinter_box()

    def quit_callback(self):
        sys.exit()

    def mk_tkinter_box(self):
        # make root tkinter box
        self.root = tkinter.Tk()
        self.root.protocol("WM_DELETE_WINDOW", self.quit_callback)
        self.main_tk_dialog =  tkinter.Frame(self.root)
        self.main_tk_dialog.pack()

        # add checkbox for draw collision box
        def cmd():
            self.master.holder.worldClass.draw_collision_boxes = not self.master.holder.worldClass.draw_collision_boxes
            
        cb1_var = tkinter.IntVar()
        cb1 = tkinter.Checkbutton(self.root, command=cmd, text="Draw Collision Boxes", variable=cb1_var)
        cb1.pack()


    def update(self):
        try:
            self.main_tk_dialog.update()
        except:
            print("dialog error")

    def finish(self):
        self.root.destroy()