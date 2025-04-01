import tkinter as tk
from tkinter import Canvas, PhotoImage
import threading
import time
import random
from enum import Enum

class Estado(Enum):
    PENSANDO = 0
    HAMBRIENTO = 1
    COMIENDO = 2

class Filosofo(threading.Thread):
    def __init__(self, id, app, tiempo_pensando=(1, 3), tiempo_comiendo=(1, 3)):
        threading.Thread.__init__(self)
        self.id = id
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
        tiempo = random.uniform(*self.tiempo_pensando)
        time.sleep(tiempo)
        
    def tomar_palillos(self):
        self.estado = Estado.HAMBRIENTO
        self.app.actualizar_estado(self.id, self.estado)
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
            time.sleep(0.1)  # Espera un poco antes de intentar de nuevo
            self.tomar_palillos()  # Intenta de nuevo
            
    def comer(self):
        self.estado = Estado.COMIENDO
        self.app.actualizar_estado(self.id, self.estado)
        tiempo = random.uniform(*self.tiempo_comiendo)
        time.sleep(tiempo)
        
    def dejar_palillos(self):
        self.app.semaforo.acquire()
        izquierdo = self.id
        derecho = (self.id + 1) % 5
        self.app.palillos_en_uso[izquierdo] = False
        self.app.palillos_en_uso[derecho] = False
        self.app.actualizar_palillos(izquierdo, derecho, False)
        self.app.semaforo.release()

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Problema de los 5 Filósofos con Palillos Chinos")
        self.root.geometry("800x600")
        
        # Semáforo para control de acceso a los palillos
        self.semaforo = threading.Semaphore(1)
        
        # Estado de los palillos (True = en uso, False = disponible)
        self.palillos_en_uso = [False] * 5
        
        # Canvas principal
        self.canvas = Canvas(root, width=800, height=600, bg="#f0f0f0")
        self.canvas.pack(fill="both", expand=True)
        
        # Cargar imágenes (debes tener estas imágenes en el mismo directorio)
        # Aquí debes proporcionar tus propias imágenes
        self.img_mesa = self.cargar_imagen("mesa.png", 400, 400)
        self.img_filosofo = [
            self.cargar_imagen("filosofo1.png", 80, 80),
            self.cargar_imagen("filosofo2.png", 80, 80),
            self.cargar_imagen("filosofo3.png", 80, 80),
            self.cargar_imagen("filosofo4.png", 80, 80),
            self.cargar_imagen("filosofo5.png", 80, 80)
        ]
        self.img_palillo = self.cargar_imagen("palillo.png", 40, 10)
        
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
        
        # Etiquetas de estado para cada filósofo
        self.etiquetas_estado = []
        for i in range(5):
            x, y = self.pos_filosofos[i]
            etiqueta = self.canvas.create_text(x, y + 60, text="Pensando", fill="black", font=("Arial", 10))
            self.etiquetas_estado.append(etiqueta)
        
        # Crear los filósofos
        self.filosofos = [Filosofo(i, self) for i in range(5)]
        
        # Iniciar los hilos de los filósofos
        for filosofo in self.filosofos:
            filosofo.start()
    
    def cargar_imagen(self, filename, width, height):
        try:
            imagen = PhotoImage(file=filename)
            return imagen.subsample(int(imagen.width() / width), int(imagen.height() / height))
        except:
            # Si no se encuentra la imagen, crea un rectángulo de placeholder
            return None
    
    def dibujar_mesa(self):
        # Dibujar la mesa en el centro del canvas
        if self.img_mesa:
            self.canvas.create_image(400, 300, image=self.img_mesa)
        else:
            # Dibujar una mesa circular simple si no hay imagen
            self.canvas.create_oval(250, 200, 550, 400, fill="#8B4513")
    
    def dibujar_filosofos(self):
        # Dibujar los filósofos alrededor de la mesa
        self.filosofos_img_ids = []
        for i in range(5):
            x, y = self.pos_filosofos[i]
            if self.img_filosofo[i]:
                img_id = self.canvas.create_image(x, y, image=self.img_filosofo[i])
            else:
                # Dibujar un círculo simple si no hay imagen
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
                # Dibujar una línea simple si no hay imagen
                x1, y1 = x-20, y
                x2, y2 = x+20, y
                img_id = self.canvas.create_line(x1, y1, x2, y2, width=3, fill="brown")
            self.palillos_img_ids.append(img_id)
    
    def actualizar_estado(self, id_filosofo, estado):
        estados = {
            Estado.PENSANDO: "Pensando",
            Estado.HAMBRIENTO: "Hambriento",
            Estado.COMIENDO: "Comiendo"
        }
        colores = {
            Estado.PENSANDO: "blue",
            Estado.HAMBRIENTO: "orange",
            Estado.COMIENDO: "green"
        }
        # Actualizar la etiqueta de estado del filósofo
        self.canvas.itemconfig(self.etiquetas_estado[id_filosofo], text=estados[estado], fill=colores[estado])
        
    def actualizar_palillos(self, izquierdo, derecho, en_uso):
        color = "red" if en_uso else "brown"
        # Si estamos usando imágenes, podríamos cambiar la opacidad o el tinte
        # Pero para la implementación simple, solo cambiamos el color si no hay imagen
        if not self.img_palillo:
            self.canvas.itemconfig(self.palillos_img_ids[izquierdo], fill=color)
            self.canvas.itemconfig(self.palillos_img_ids[derecho], fill=color)
        
        # Forzar actualización del canvas
        self.root.update()

if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()
