import tkinter as tk
from tkinter import Canvas, PhotoImage, Frame, Label
import threading
import time
from enum import Enum

class Estado(Enum):
    PENSANDO = 0
    COMIENDO = 1

class Filosofo(threading.Thread):
    def __init__(self, id, nombre, app, tiempo_pensando=5, tiempo_comiendo=5):
        threading.Thread.__init__(self)
        self.id = id
        self.nombre = nombre
        self.app = app
        self.estado = Estado.PENSANDO
        self.tiempo_pensando = tiempo_pensando
        self.tiempo_comiendo = tiempo_comiendo
        self.daemon = True
        
    def run(self):
        while True:
            self.pensar()
            self.tomar_palillos()
            self.comer()
            self.dejar_palillos()
            
    def pensar(self):
        self.estado = Estado.PENSANDO
        self.app.actualizar_estado(self.id, self.estado)
        time.sleep(self.tiempo_pensando)
        
    def tomar_palillos(self):
        
        self.app.semaforo.acquire()
        # Intenta tomar ambos palillos
        izquierdo = self.id
        derecho = (self.id + 1) % 5
        
        # Verifica si ambos palillos están disponibles
        if (not self.app.palillos_en_uso[izquierdo] and 
            not self.app.palillos_en_uso[derecho]):
            self.app.palillos_en_uso[izquierdo] = True
            self.app.palillos_en_uso[derecho] = True
            self.app.actualizar_palillos(izquierdo, derecho, True)
            self.app.semaforo.release()
        else:
            self.app.semaforo.release()
            time.sleep(0.5)  # Espera un poco antes de intentar de nuevo
            self.tomar_palillos()  # Intenta de nuevo
            
    def comer(self):
        self.estado = Estado.COMIENDO
        self.app.actualizar_estado(self.id, self.estado)
        time.sleep(self.tiempo_comiendo)
        
    def dejar_palillos(self):
        self.app.semaforo.acquire()
        izquierdo = self.id
        derecho = (self.id + 1) % 5
        self.app.palillos_en_uso[izquierdo] = False
        self.app.palillos_en_uso[derecho] = False
        self.app.actualizar_palillos(izquierdo, derecho, False)
        self.app.semaforo.release()

# Este es el código de la interfaz gráfica
class App:
    def __init__(self, root):
        self.root = root
        self.root.title("5 Filósofos")
        self.root.geometry("1000x600")
        
        # Nombres de los filósofos
        self.nombres_filosofos = [
            "Sócrates", 
            "Platón", 
            "Aristóteles", 
            "Confucio", 
            "Lao Tse"
        ]
        
        # Semáforo para control de acceso a los palillos
        self.semaforo = threading.Semaphore(1)
        
        # Estado de los palillos (True = en uso, False = disponible)
        self.palillos_en_uso = [False] * 5
        
        # Información en el lado izquierdo
        self.panel_info = Frame(root, width=200, bg="#e0e0e0", padx=10, pady=10)
        self.panel_info.pack(side="left", fill="y")
        
        # Título del panel
        titulo = Label(self.panel_info, text="ESTADO DE FILÓSOFOS", font=("Arial", 12, "bold"), bg="#e0e0e0")
        titulo.pack(pady=(0, 10))
        
        # Frame para cada filósofo en el panel
        self.frames_info_filosofos = []
        self.labels_nombre_filosofos = []
        self.labels_estado_filosofos = []
        
        for i in range(5):
            frame = Frame(self.panel_info, bg="#d0d0d0", padx=5, pady=5, borderwidth=1, relief="solid")
            frame.pack(fill="x", pady=5)
            
            lbl_nombre = Label(frame, text=self.nombres_filosofos[i], font=("Arial", 10, "bold"), bg="#d0d0d0")
            lbl_nombre.pack(pady=(0, 5))
            
            lbl_estado = Label(frame, text="Pensando", font=("Arial", 9), bg="#d0d0d0", fg="blue")
            lbl_estado.pack()
            
            self.frames_info_filosofos.append(frame)
            self.labels_nombre_filosofos.append(lbl_nombre)
            self.labels_estado_filosofos.append(lbl_estado)
        
        # Frame para la visualización gráfica
        self.frame_visual = Frame(root)
        self.frame_visual.pack(side="right", fill="both", expand=True)
        
        # Canvas principal
        self.canvas = Canvas(self.frame_visual, width=800, height=600, bg="#f0f0f0")
        self.canvas.pack(fill="both", expand=True)
        
        # Cargar imágenes
        self.img_mesa = self.cargar_imagen("mesa.png", 400, 400)
        self.img_filosofo = [
            self.cargar_imagen("filosofo1.png", 80, 80),
            self.cargar_imagen("filosofo2.png", 80, 80),
            self.cargar_imagen("filosofo3.png", 80, 80),
            self.cargar_imagen("filosofo4.png", 80, 80),
            self.cargar_imagen("filosofo5.png", 80, 80)
        ]
        # Palillos
        self.img_palillo = self.cargar_imagen("palillo.png", 60, 15)
        
        # Fondos de colores para los filósofos
        self.filosofos_fondos = []
        
        # Posiciones de los filósofos (centro x, centro y)
        self.pos_filosofos = [
            (400, 150),  # Arriba
            (550, 250),  # Derecha arriba
            (500, 400),  # Derecha abajo
            (300, 400),  # Izquierda abajo
            (250, 250)   # Izquierda arriba
        ]
        
        # Posiciones de los palillos (centro x, centro y, ángulo)
        self.pos_palillos = [
            (475, 200, 45),     # Entre filósofo 0 y 1
            (525, 325, 90),     # Entre filósofo 1 y 2
            (400, 425, 135),    # Entre filósofo 2 y 3
            (275, 325, 90),     # Entre filósofo 3 y 4
            (325, 200, 45)      # Entre filósofo 4 y 0
        ]
        
        # Dibujar mesa, filósofos y palillos
        self.dibujar_mesa()
        self.dibujar_filosofos()
        self.dibujar_palillos()
        
        # Etiquetas de estado para cada filósofo en el canvas
        self.etiquetas_estado = []
        for i in range(5):
            x, y = self.pos_filosofos[i]
            etiqueta = self.canvas.create_text(x, y + 60, text=self.nombres_filosofos[i], fill="black", font=("Arial", 10, "bold"))
            self.etiquetas_estado.append(etiqueta)
        
        # Crear los filósofos
        self.filosofos = [Filosofo(i, self.nombres_filosofos[i], self) for i in range(5)]
        
        # Iniciar los hilos de los filósofos
        for filosofo in self.filosofos:
            filosofo.start()
    
    def cargar_imagen(self, filename, width, height):
        try:
            imagen = PhotoImage(file=filename)
            return imagen.subsample(int(imagen.width() / width), int(imagen.height() / height))
        except:
            
            return None
    
    def dibujar_mesa(self):
        
        if self.img_mesa:
            self.canvas.create_image(400, 300, image=self.img_mesa)
        else:
            
            self.canvas.create_oval(250, 200, 550, 400, fill="#8B4513")
    
    def dibujar_filosofos(self):
        # Dibujar los filósofos alrededor de la mesa con fondos de colores
        self.filosofos_img_ids = []
        
        for i in range(5):
            x, y = self.pos_filosofos[i]
            
            # Crear un fondo circular para cada filósofo
            fondo = self.canvas.create_oval(x-40, y-40, x+40, y+40, fill="#d0d0d0", outline="")
            self.filosofos_fondos.append(fondo)
            
            if self.img_filosofo[i]:
                img_id = self.canvas.create_image(x, y, image=self.img_filosofo[i])
            else:
                
                img_id = self.canvas.create_oval(x-30, y-30, x+30, y+30, fill="#FFD700")
            self.filosofos_img_ids.append(img_id)
    
    def dibujar_palillos(self):
        # Dibujar los palillos entre los filósofos
        self.palillos_img_ids = []
        for i in range(5):
            x, y, angulo = self.pos_palillos[i]
            if self.img_palillo:
                img_id = self.canvas.create_image(x, y, image=self.img_palillo)
            else:
                
                x1, y1 = x-30, y
                x2, y2 = x+30, y
                img_id = self.canvas.create_line(x1, y1, x2, y2, width=5, fill="brown")
            self.palillos_img_ids.append(img_id)
    
    def actualizar_estado(self, id_filosofo, estado):
        estados = {
            Estado.PENSANDO: "Pensando",
            Estado.COMIENDO: "Comiendo"
        }
        colores = {
            Estado.PENSANDO: "blue",
            Estado.COMIENDO: "green"
        }
        
        # Colores de fondo para los filósofos en el canvas
        bg_colores = {
            Estado.PENSANDO: "#d0d0d0",  
            Estado.COMIENDO: "#c0ffc0"   
        }
        
        # Actualizar el fondo del filósofo en el canvas
        self.canvas.itemconfig(self.filosofos_fondos[id_filosofo], fill=bg_colores[estado])
        
        # Actualizar la etiqueta de estado del filósofo en el canvas
        self.canvas.itemconfig(self.etiquetas_estado[id_filosofo], text=f"{self.nombres_filosofos[id_filosofo]}\n{estados[estado]}")
        
        # Actualizar el label en el panel de información
        self.labels_estado_filosofos[id_filosofo].config(text=estados[estado], fg=colores[estado])
        
        # Cambiar el color de fondo del frame según el estado
        self.frames_info_filosofos[id_filosofo].config(bg=bg_colores[estado])
        self.labels_nombre_filosofos[id_filosofo].config(bg=bg_colores[estado])
        self.labels_estado_filosofos[id_filosofo].config(bg=bg_colores[estado])
        
        # Forzar actualización de la interfaz
        self.root.update()
        
    def actualizar_palillos(self, izquierdo, derecho, en_uso):
        color = "red" if en_uso else "brown"
       
        if not self.img_palillo:
            self.canvas.itemconfig(self.palillos_img_ids[izquierdo], fill=color)
            self.canvas.itemconfig(self.palillos_img_ids[derecho], fill=color)
        
        # Forzar actualización del canvas
        self.root.update()

if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()