import flet as ft
from datetime import datetime 
import time 

class Pomodoro:
    running_rest=False
    resting=0
    studies=0
    studies_count=0
    start_point=0
    running=True
    def __init__(self,page,session_text,pb,txt_number,audio1,audio2,audio3):
        self.session_text=session_text
        self.page=page
        self.pb=pb
        self.txt_number=txt_number
        self.audio1=audio1
        self.audio2=audio2
        self.audio3=audio3
        
    async def start_pomodorro(self,e):
        self.session_text.size=15
        self.session_text.weight=ft.FontWeight.W_400
        self.session_text.bgcolor=ft.colors.WHITE24
        self.session_text.color=ft.colors.WHITE70
        self.running=True
        if self.studies==0:
            sessions="Let's start studying..."
        else:
            sessions=f'You have done {self.studies} session until now, keep it up champ!'
        self.session_text.value= sessions
        self.start_point+=1
        self.pb.value=0
        if self.start_point<=1:
            await self.page.add_async(ft.Row( [self.pb],alignment=ft.MainAxisAlignment.CENTER))
            await self.page.add_async(ft.Row([self.session_text],alignment=ft.MainAxisAlignment.CENTER))
        mins,secs=self.txt_number.value.split(':')
        t=int(mins)*60+int(secs)
        total=t

        i=0
        while t and self.running:
                mins, seconds = divmod(t, 60)
                timer =  "{:02d}:{:02d}".format(mins,seconds)
                time.sleep(1)
                t -= 1
                self.txt_number.value=str(timer)
                await self.page.update_async()
                if i==0:
                    await self.audio1.play_async()             
                else:
                    await self.audio2.play_async()
                    
                i+=1
                self.pb.value = i * (1/int(total))
                await self.page.update_async()
        if t<1:
            self.studies+=1
        await self.audio3.play_async()
        if self.resting==0:
            await self.page.add_async(ft.Row([ft.ElevatedButton(text="Take a Break",on_click=self.take_rest)],alignment=ft.MainAxisAlignment.CENTER))
            
        self.resting+=1
        
    async def take_rest(self,e):
        self.running=False
        self.pb.value=0
        if self.studies%3==0 and self.studies!=0:
            self.txt_number.value="10:00"
        else:
            self.txt_number.value="05:00"
        await self.page.update_async()

        mins,secs=self.txt_number.value.split(':')
        t=int(mins)*60+int(secs)
        total=t
        i=0
        self.running_rest=True
        while t and self.running_rest:
                mins, seconds = divmod(t, 60)
                timer = "{:02d}:{:02d}".format(mins,seconds)
                time.sleep(1)
                t -= 1
                self.txt_number.value=str(timer)
                await self.page.update_async()
                if i==0:
                    self.audio1.play_async()              
                else:
                    self.audio2.play_async()
                    
                i+=1
                self.pb.value = i * (1/int(total))
                await self.page.update_async()
        await self.audio3.play_async()
        self.running_rest=False
        self.txt_number.value="25:00"
        await self.page.update_async()
        
        



    async def restart(self,e):

        self.pb.value=0
        self.running_rest=False
        self.txt_number.value="25:00"
        await self.page.update_async()
        self.running=False
        
    async def pause_timer(self,e):
        self.running=False
        await self.audio2.pause_async()
        await self.audio3.play_async()
        self.session_text.value="Don't Stop studying now! You can do better..."
        self.session_text.size+=5
        self.session_text.weight=ft.FontWeight.BOLD
        self.session_text.color=ft.colors.RED_600
        self.session_text.bgcolor=ft.colors.AMBER
        await self.page.update_async()
        return self.running




class Task(ft.UserControl):
    def __init__(self, task_name, task_status_change, task_delete):
        super().__init__()
        self.completed = False
        self.task_name = task_name
        self.task_status_change = task_status_change
        self.task_delete = task_delete

    def build(self):
        self.display_task = ft.Checkbox(
            value=False, label=self.task_name, on_change=self.status_changed
        )
        self.edit_name = ft.TextField(expand=1)

        self.display_view = ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                self.display_task,
                ft.Row(
                    spacing=0,
                    controls=[
                        ft.IconButton(
                            icon=ft.icons.CREATE_OUTLINED,
                            tooltip="Edit To-Do",
                            on_click=self.edit_clicked,
                        ),
                        ft.IconButton(
                            ft.icons.DELETE_OUTLINE,
                            tooltip="Delete To-Do",
                            on_click=self.delete_clicked,
                        ),
                    ],
                ),
            ],
        )

        self.edit_view = ft.Row(
            visible=False,
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                self.edit_name,
                ft.IconButton(
                    icon=ft.icons.DONE_OUTLINE_OUTLINED,
                    icon_color=ft.colors.GREEN,
                    tooltip="Update To-Do",
                    on_click=self.save_clicked,
                ),
            ],
        )
        return ft.Column(controls=[self.display_view, self.edit_view])

    async def edit_clicked(self, e):
        self.edit_name.value = self.display_task.label
        self.display_view.visible = False
        self.edit_view.visible = True
        await self.update_async()

    async def save_clicked(self, e):
        self.display_task.label = self.edit_name.value
        self.display_view.visible = True
        self.edit_view.visible = False
        await self.update_async()

    async def status_changed(self, e):
        self.completed = self.display_task.value
        await self.task_status_change(self)

    async def delete_clicked(self, e):
        await self.task_delete(self)


class TodoApp(ft.UserControl):
    
    
    # def __init__(self,page):
    #     self.page=page
    
    def build(self):
       
        
        
        
        
        self.new_task = ft.TextField(
            hint_text="What needs to be done?", on_submit=self.add_clicked, expand=True
        )
        self.tasks = ft.Column()

        self.filter = ft.Tabs(
            scrollable=False,
            selected_index=0,
            on_change=self.tabs_changed,
            tabs=[ft.Tab(text="all"), ft.Tab(text="active"), ft.Tab(text="completed")],
        )

        self.items_left = ft.Text("0 items left")

        # application's root control (i.e. "view") containing all other controls
        return ft.Column(
            width=600,
            controls=[
                ft.Row(
                    [ft.Text(value="Todos", style=ft.TextThemeStyle.HEADLINE_MEDIUM)],
                    alignment=ft.MainAxisAlignment.CENTER,
                ),
                ft.Row(
                    controls=[
                        self.new_task,
                        ft.FloatingActionButton(
                            icon=ft.icons.ADD, on_click=self.add_clicked
                        ),
                    ],
                ),
                ft.Column(
                    spacing=25,
                    controls=[
                        self.filter,
                        self.tasks,
                        ft.Row(
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                            vertical_alignment=ft.CrossAxisAlignment.CENTER,
                            controls=[
                                self.items_left,
                                ft.OutlinedButton(
                                    text="Clear completed", on_click=self.clear_clicked
                                ),
                            ],
                        ),
                    ],
                ),
                ft.Row(),
                ft.Row(
                    [ft.Text("Pomodoro Timer",size=40)],alignment=ft.MainAxisAlignment.CENTER
                    )
            ],
        )

    async def add_clicked(self, e):
        if self.new_task.value:
            task = Task(self.new_task.value, self.task_status_change, self.task_delete)
            self.tasks.controls.append(task)
            self.new_task.value = ""
            await self.new_task.focus_async()
            await self.update_async()

    async def task_status_change(self, task):
        await self.update_async()

    async def task_delete(self, task):
        self.tasks.controls.remove(task)
        await self.update_async()

    async def tabs_changed(self, e):
        await self.update_async()

    async def clear_clicked(self, e):
        for task in self.tasks.controls[:]:
            if task.completed:
                await self.task_delete(task)

    async def update_async(self):
        status = self.filter.tabs[self.filter.selected_index].text
        count = 0
        for task in self.tasks.controls:
            task.visible = (
                status == "all"
                or (status == "active" and task.completed == False)
                or (status == "completed" and task.completed)
            )
            if not task.completed:
                count += 1
        self.items_left.value = f"{count} active item(s) left"
        await super().update_async()


async def main(page: ft.Page):
    page.title = "ToDo App"
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.scroll = ft.ScrollMode.ADAPTIVE
    
    session_text=ft.Text(value='',size=15, text_align=ft.TextAlign.CENTER, width=200,bgcolor=ft.colors.WHITE60,weight=ft.FontWeight.W_400)
    pb= ft.ProgressBar(width=700,height=10)
    txt_number = ft.Text(value="25:00",size=50, text_align=ft.TextAlign.CENTER, width=300,bgcolor=ft.colors.RED,weight=ft.FontWeight.W_100)
    first_tick='first_tick.mp3'
    normal_tick='normal_tick.mp3'
    final_tick='final_tick.mp3'
    audio1=ft.Audio(src=first_tick)
    audio2=ft.Audio(src=normal_tick)
    audio3=ft.Audio(src=final_tick)
    page.overlay.append(audio1)
    page.overlay.append(audio2)
    page.overlay.append(audio3)
    # pb = ft.ProgressBar(width=700,height=10)
    

    
    
    now=datetime.now()
    hour_now=now.strftime("%H")
    am_or_pm=now.strftime("%p")
    # if am_or_pm=='AM'and int(hour_now)>=6:
    #     page.bgcolor="WHITE"
    # elif am_or_pm=='AM' and int(hour_now)<6:
    #     page.bgcolor='BLACK'
    # elif am_or_pm=='PM' and int(hour_now)>=6:
    #     page.bgcolor='BLACK'
    # elif am_or_pm=='PM' and int(hour_now)<6:
    #     page.bgcolor == 'WHITE'
    

    await page.add_async(TodoApp())
    await page.add_async(ft.Row([ft.Image("tomato_food_20602.ico")],alignment=ft.MainAxisAlignment.CENTER))
    
    
    
    session_text=ft.Text(value='',size=15, text_align=ft.TextAlign.CENTER, width=200,bgcolor=ft.colors.WHITE60,weight=ft.FontWeight.W_400)
    Pomodoro_timer=Pomodoro(page, session_text, pb, txt_number, audio1, audio2, audio3)
    await page.add_async(
        ft.Row(
            [
                ft.IconButton(ft.icons.PLAY_ARROW_ROUNDED,width=50,height=100, on_click=Pomodoro_timer.start_pomodorro),
                txt_number,
                ft.IconButton(ft.icons.PAUSE, on_click=Pomodoro_timer.pause_timer),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
        ),
        ft.Row([
                ft.IconButton(ft.icons.RESTART_ALT, on_click=Pomodoro_timer.restart),    
            ],alignment=ft.MainAxisAlignment.CENTER),   
        
                    
    )


ft.app(main)