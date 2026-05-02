use pyo3::prelude::*;

mod simulation;

#[pymodule]
fn aether_core(_py: Python, m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_class::<simulation::Simulacion>()?;
    Ok(())
}
