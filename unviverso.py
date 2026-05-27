import pygame
import math
import random
import sys

# --- CONFIGURACIÓN DE LA PANTALLA ---
ANCHO, ALTO = 1024, 768
FPS = 60

# --- COLORES ---
NEGRO = (10, 10, 15)
BLANCO = (255, 255, 255)
AZUL = (50, 150, 255)
ROJO = (255, 80, 80)
VERDE = (80, 255, 80)
AMARILLO = (255, 220, 50)

class Camara:
    """Maneja la matriz de vista 3D, rotación y proyección del espacio."""
    def __init__(self):
        self.x, self.y, self.z = 0, 0, -600
        self.rot_x, self.rot_y = 0, 0
        self.fov = 400  # Distancia focal de proyección

    def proyectar(self, px, py, pz):
        """Transforma coordenadas 3D del espacio a coordenadas 2D de la pantalla."""
        # Traslación respecto a la cámara
        cx, cy, cz = px - self.x, py - self.y, pz - self.z
        
        # Rotación en el eje Y (Giro horizontal)
        rad_y = math.radians(self.rot_y)
        cos_y, sin_y = math.cos(rad_y), math.sin(rad_y)
        x1 = cx * cos_y - cz * sin_y
        z1 = cx * sin_y + cz * cos_y
        
        # Rotación en el eje X (Inclinación vertical)
        rad_x = math.radians(self.rot_x)
        cos_x, sin_x = math.cos(rad_x), math.sin(rad_x)
        y2 = cy * cos_x - z1 * sin_x
        z2 = cy * sin_x + z1 * cos_x
        
        if z2 <= 10:  # Evita división por cero u objetos detrás de la cámara
            return None
            
        # Proyección de perspectiva matemática
        sx = int((x1 * self.fov) / z2 + ANCHO / 2)
        sy = int((y2 * self.fov) / z2 + ALTO / 2)
        return sx, sy, z2

class CuerpoCeleste:
    """Entidad física interactiva que ejerce gravedad y simula órbita."""
    def __init__(self, x, y, z, vx, vy, vz, masa, radio, color, nombre):
        self.x, self.y, self.z = x, y, z
        self.vx, self.vy, self.vz = vx, vy, vz
        self.masa = masa
        self.radio = radio
        self.color = color
        self.nombre = nombre
        self.historial_trayectoria = []

    def aplicar_gravedad(self, otros_cuerpos, G=0.1):
        """Calcula la aceleración basada en la Ley de Gravitación de Newton en 3D."""
        for cuerpo in otros_cuerpos:
            if cuerpo == self:
                continue
            dx = cuerpo.x - self.x
            dy = cuerpo.y - self.y
            dz = cuerpo.z - self.z
            distancia = math.sqrt(dx**2 + dy**2 + dz**2)
            
            if distancia < (self.radio + cuerpo.radio): # Colisión elemental
                continue
                
            # Fuerza de atracción
            fuerza = (G * self.masa * cuerpo.masa) / (distancia**2)
            # Componentes vectoriales de la aceleración
            self.vx += (fuerza * dx) / (self.masa * distancia)
            self.vy += (fuerza * dy) / (self.masa * distancia)
            self.vz += (fuerza * dz) / (self.masa * distancia)

    def actualizar(self):
        """Actualiza la posición tridimensional mediante integración física de Euler."""
        self.x += self.vx
        self.y += self.vy
        self.z += self.vz
        
        # Registra la estela del camino orbital
        self.historial_trayectoria.append((self.x, self.y, self.z))
        if len(self.historial_trayectoria) > 150:
            self.historial_trayectoria.pop(0)

def generar_estrellas_fondo(cantidad=300):
    """Genera coordenadas procedimentales para el campo de estrellas profundo."""
    estrellas = []
    for _ in range(cantidad):
        x = random.randint(-2000, 2000)
        y = random.randint(-2000, 2000)
        z = random.randint(-2000, 2000)
        estrellas.append((x, y, z))
    return estrellas

def main():
    pygame.init()
    pantalla = pygame.display.set_mode((ANCHO, ALTO))
    pygame.display.set_caption("Motor Físico Espacial 3D Avanzado")
    reloj = pygame.time.Clock()
    fuente = pygame.font.SysFont("Courier", 14)
    
    camara = Camara()
    estrellas = generar_estrellas_fondo()
    
    # --- CREACIÓN DEL SISTEMA SOLAR SINTÉTICO (Posición, Velocidad Vectorial, Masa, Radio, Color) ---
    estrella_central = CuerpoCeleste(0, 0, 0, 0, 0, 0, 50000, 30, AMARILLO, "Estrella Alfa")
    planeta_azul = CuerpoCeleste(250, 0, 0, 0, 0, 4.2, 800, 12, AZUL, "Planeta Océano")
    planeta_rojo = CuerpoCeleste(-380, 0, 0, 0, 0, -3.4, 600, 9, ROJO, "Planeta Desierto")
    luna_azul = CuerpoCeleste(250, 35, 0, 1.8, 0, 4.2, 5, 3, BLANCO, "Satélite")
    
    cuerpos = [estrella_central, planeta_azul, planeta_rojo, luna_azul]
    
    corriendo = True
    while corriendo:
        pantalla.fill(NEGRO)
        
        # --- ENTRADAS DE USUARIO (Controles de Navegación 3D de la Cámara) ---
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                corriendo = False
                
        teclas = pygame.key.get_pressed()
        if teclas[pygame.K_w]: camara.z += 8   # Avanzar
        if teclas[pygame.K_s]: camara.z -= 8   # Retroceder
        if teclas[pygame.K_a]: camara.x -= 8   # Desplazarse izquierda
        if teclas[pygame.K_d]: camara.x += 8   # Desplazarse derecha
        if teclas[pygame.K_UP]: camara.rot_x -= 1.5 # Mirar arriba
        if teclas[pygame.K_DOWN]: camara.rot_x += 1.5 # Mirar abajo
        if teclas[pygame.K_LEFT]: camara.rot_y -= 1.5 # Mirar izquierda
        if teclas[pygame.K_RIGHT]: camara.rot_y += 1.5 # Mirar derecha

        # --- ACTUALIZACIÓN DE FÍSICAS MÚLTIPLES ---
        for cuerpo in cuerpos:
            cuerpo.aplicar_gravedad(cuerpos)
        for cuerpo in cuerpos:
            cuerpo.actualizar()
            
        # --- RENDERIZADO DEL ENTORNO ---
        # 1. Dibujar el fondo infinito de estrellas
        for estrella in estrellas:
            proy = camara.proyectar(estrella[0], estrella[1], estrella[2])
            if proy:
                sx, sy, cz = proy
                # Efecto de paralaje: estrellas más lejanas se ven más pequeñas y tenues
                brillo = max(50, min(255, int(255 - cz * 0.05)))
                pygame.draw.circle(pantalla, (brillo, brillo, brillo), (sx, sy), 1)

        # Ordenar cuerpos por profundidad Z (Pintar primero lo lejano para oclusión correcta)
        cuerpos_ordenados = sorted(
            [c for c in cuerpos if camara.proyectar(c.x, c.y, c.z) is not None],
            key=lambda c: camara.proyectar(c.x, c.y, c.z)[2],
            reverse=True
        )

        # 2. Dibujar órbitas e hilos de trayectoria vectoriales
        for cuerpo in cuerpos:
            if len(cuerpo.historial_trayectoria) > 1:
                puntos_pantalla = []
                for nodo in cuerpo.historial_trayectoria:
                    proy_nodo = camara.proyectar(nodo[0], nodo[1], nodo[2])
                    if proy_nodo:
                        puntos_pantalla.append((proy_nodo[0], proy_nodo[1]))
                if len(puntos_pantalla) > 1:
                    pygame.draw.lines(pantalla, [c // 3 for c in cuerpo.color], False, puntos_pantalla, 1)

        # 3. Dibujar los cuerpos celestes (Esferas Proyectadas)
        for cuerpo in cuerpos_ordenados:
            sx, sy, cz = camara.proyectar(cuerpo.x, cuerpo.y, cuerpo.z)
            # Escalar el tamaño visual basado en la distancia radial
            radio_proyectado = max(1, int((cuerpo.radio * camara.fov) / cz))
            
            # Dibujar volumen básico
            pygame.draw.circle(pantalla, cuerpo.color, (sx, sy), radio_proyectado)
            
            # Etiqueta de telemetría de interfaz
            texto = fuente.render(f"{cuerpo.nombre}", True, VERDE)
            pantalla.blit(texto, (sx + radio_proyectado + 5, sy - 5))

        # --- INTERFAZ GRÁFICA (HUD) ---
        hud_controles = [
            "CONTROLES DEL ESPACIO 3D:",
            "Mover Cámara: W, A, S, D",
            "Rotar Cámara: Flechas Dirección",
            f"Posición Cam: X:{int(camara.x)} Y:{int(camara.y)} Z:{int(camara.z)}",
            f"FPS: {int(reloj.get_fps())}"
        ]
        for i, linea in enumerate(hud_controles):
            img_texto = fuente.render(linea, True, BLANCO)
            pantalla.blit(img_texto, (15, 15 + i * 20))

        pygame.display.flip()
        reloj.tick(FPS)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
