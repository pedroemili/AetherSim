use pyo3::prelude::*;
use rand::Rng;
use numpy::{IntoPyArray, PyArray1};

#[pyclass]
pub struct Simulacion {
    posiciones: Vec<(f32, f32)>,
    velocidades: Vec<(f32, f32)>,
    num_particulas: usize,
    ancho: f32,
    alto: f32,
}

#[pymethods]
impl Simulacion {
    #[new]
    pub fn new(num_particulas: usize, ancho: f32, alto: f32) -> Self {
        let mut rng = rand::thread_rng();
        let mut posiciones = Vec::with_capacity(num_particulas);
        let mut velocidades = Vec::with_capacity(num_particulas);

        for _ in 0..num_particulas {
            posiciones.push((
                rng.gen_range(0.0..ancho),
                rng.gen_range(0.0..alto),
            ));
            velocidades.push((
                rng.gen_range(-1.0..1.0),
                rng.gen_range(-1.0..1.0),
            ));
        }

        Self {
            posiciones,
            velocidades,
            num_particulas,
            ancho,
            alto,
        }
    }

    #[pyo3(signature = (dt, foco_x, foco_y, fuerza_foco, friccion))]
    pub fn paso(&mut self, dt: f32, foco_x: f32, foco_y: f32, fuerza_foco: f32, friccion: f32) {
        for i in 0..self.num_particulas {
            let (mut px, mut py) = self.posiciones[i];
            let (mut vx, mut vy) = self.velocidades[i];

            let dx = foco_x - px;
            let dy = foco_y - py;
            let dist_sq = dx * dx + dy * dy;
            let dist = dist_sq.sqrt();

            // Aplicar fuerza si la distancia no es muy pequeña
            if dist > 1.0 {
                //  Crea una estética de gravedad interesante
                let fuerza = fuerza_foco / (dist.max(10.0));
                vx += (dx / dist) * fuerza * dt;
                vy += (dy / dist) * fuerza * dt;
            }

            vx *= friccion;
            vy *= friccion;

            px += vx * dt;
            py += vy * dt;

            // Rebote con las paredes
            if px < 0.0 {
                px = 0.0;
                vx = -vx * 0.6;
            } else if px > self.ancho {
                px = self.ancho;
                vx = -vx * 0.6;
            }

            if py < 0.0 {
                py = 0.0;
                vy = -vy * 0.6;
            } else if py > self.alto {
                py = self.alto;
                vy = -vy * 0.6;
            }

            self.posiciones[i] = (px, py);
            self.velocidades[i] = (vx, vy);
        }
    }

    pub fn obtener_posiciones<'py>(&self, py: Python<'py>) -> Bound<'py, PyArray1<f32>> {
        let mut pos_planas = Vec::with_capacity(self.num_particulas * 2);
        for &(x, y) in &self.posiciones {
            pos_planas.push(x);
            pos_planas.push(y);
        }
        pos_planas.into_pyarray_bound(py)
    }

    pub fn agregar_particulas(&mut self, cantidad: usize, x: f32, y: f32) {
        let mut rng = rand::thread_rng();
        let max_particulas: usize = 100000;
        let cantidad_agregar = cantidad.min(max_particulas.saturating_sub(self.num_particulas));
        
        for _ in 0..cantidad_agregar {
            let dispersion = 15.0;
            self.posiciones.push((x + rng.gen_range(-dispersion..dispersion), y + rng.gen_range(-dispersion..dispersion)));
            self.velocidades.push((
                rng.gen_range(-200.0..200.0),
                rng.gen_range(-200.0..200.0),
            ));
        }
        self.num_particulas += cantidad_agregar;
    }
}
