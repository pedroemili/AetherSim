use wasm_bindgen::prelude::*;
use web_sys::CanvasRenderingContext2d;
use rand::Rng;

#[wasm_bindgen]
pub struct Particle {
    x: f64,
    y: f64,
    vx: f64,
    vy: f64,
    radius: f64,
    color: String,
}

#[wasm_bindgen]
impl Particle {
    pub fn new(x: f64, y: f64, vx: f64, vy: f64, radius: f64, color: String) -> Particle {
        Particle { x, y, vx, vy, radius, color }
    }

    pub fn update(&mut self, width: f64, height: f64, gesture_x: f64, gesture_y: f64, gesture_strength: f64) {
        // Apply gesture force
        let dx = self.x - gesture_x;
        let dy = self.y - gesture_y;
        let dist = (dx * dx + dy * dy).sqrt();
        
        if dist > 0.0 && gesture_strength > 0.0 {
            let force = gesture_strength / (dist * dist + 100.0);
            self.vx += (dx / dist) * force;
            self.vy += (dy / dist) * force;
        }

        // Update position
        self.x += self.vx;
        self.y += self.vy;

        // Apply friction
        self.vx *= 0.98;
        self.vy *= 0.98;

        // Boundary collision
        if self.x - self.radius < 0.0 || self.x + self.radius > width {
            self.vx *= -0.8;
            self.x = self.x.max(self.radius).min(width - self.radius);
        }
        if self.y - self.radius < 0.0 || self.y + self.radius > height {
            self.vy *= -0.8;
            self.y = self.y.max(self.radius).min(height - self.radius);
        }
    }

    pub fn draw(&self, ctx: &CanvasRenderingContext2d) {
        ctx.begin_path();
        ctx.arc(self.x, self.y, self.radius, 0.0, 2.0 * std::f64::consts::PI).unwrap();
        ctx.set_fill_style(&JsValue::from_str(&self.color));
        ctx.fill();
    }

    #[wasm_bindgen(getter)]
    pub fn x(&self) -> f64 { self.x }

    #[wasm_bindgen(getter)]
    pub fn y(&self) -> f64 { self.y }

    #[wasm_bindgen(setter)]
    pub fn set_x(&mut self, x: f64) { self.x = x; }

    #[wasm_bindgen(setter)]
    pub fn set_y(&mut self, y: f64) { self.y = y; }
}

#[wasm_bindgen]
pub struct ParticleSystem {
    particles: Vec<Particle>,
    width: f64,
    height: f64,
}

#[wasm_bindgen]
impl ParticleSystem {
    #[wasm_bindgen(constructor)]
    pub fn new(width: f64, height: f64, count: usize) -> ParticleSystem {
        let mut rng = rand::thread_rng();
        let mut particles = Vec::with_capacity(count);

        let colors = vec![
            "#FF6B6B".to_string(),
            "#4ECDC4".to_string(),
            "#45B7D1".to_string(),
            "#FFA07A".to_string(),
            "#98D8C8".to_string(),
            "#F7DC6F".to_string(),
        ];

        for _ in 0..count {
            let x = rng.gen_range(0.0..width);
            let y = rng.gen_range(0.0..height);
            let vx = rng.gen_range(-2.0..2.0);
            let vy = rng.gen_range(-2.0..2.0);
            let radius = rng.gen_range(3.0..8.0);
            let color = colors[rng.gen_range(0..colors.len())].clone();

            particles.push(Particle::new(x, y, vx, vy, radius, color));
        }

        ParticleSystem { particles, width, height }
    }

    pub fn update(&mut self, gesture_x: f64, gesture_y: f64, gesture_strength: f64) {
        for particle in &mut self.particles {
            particle.update(self.width, self.height, gesture_x, gesture_y, gesture_strength);
        }
    }

    pub fn render(&self, ctx: &CanvasRenderingContext2d) {
        ctx.clear_rect(0.0, 0.0, self.width, self.height);
        for particle in &self.particles {
            particle.draw(ctx);
        }
    }

    pub fn add_particle(&mut self, x: f64, y: f64) {
        let mut rng = rand::thread_rng();
        let vx = rng.gen_range(-2.0..2.0);
        let vy = rng.gen_range(-2.0..2.0);
        let radius = rng.gen_range(3.0..8.0);
        let colors = vec!["#FF6B6B", "#4ECDC4", "#45B7D1", "#FFA07A", "#98D8C8", "#F7DC6F"];
        let color = colors[rng.gen_range(0..colors.len())].to_string();
        
        self.particles.push(Particle::new(x, y, vx, vy, radius, color));
    }

    pub fn get_particle_count(&self) -> usize {
        self.particles.len()
    }
}
