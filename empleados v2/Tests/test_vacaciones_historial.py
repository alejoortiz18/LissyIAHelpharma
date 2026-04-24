"""
Pruebas funcionales — Historial de Eventos y Cálculo de Vacaciones
Sistema: GestiónRH — Administración de Empleados

TC-VAC-01  Columna Días visible en tab Historial
TC-VAC-02  Valor de Días coincide con FechaFin - FechaInicio + 1
TC-VAC-03  Filtros Desde/Hasta presentes en tab Historial
TC-VAC-04  Filtrar por rango muestra solo eventos dentro del rango
TC-VAC-05  Filtrar por rango sin eventos muestra estado vacío
TC-VAC-06  Botón Limpiar restaura la tabla sin filtros
TC-VAC-07  Resumen por tipo visible cuando hay eventos
TC-VAC-08  Resumen refleja solo los eventos del período filtrado
TC-VAC-09  Vacaciones disponibles muestra valor numérico (FechaInicioContrato definida)
TC-VAC-10  Vacaciones disponibles muestra "—" cuando FechaInicioContrato es NULL
"""

import pytest
from helpers import BASE_URL, hacer_login, hacer_logout

CORREO_JEFE = "carlos.rodriguez@yopmail.com"
PASSWORD = "Usuario1"

# ─── Helpers ─────────────────────────────────────────────────────────────────

def _login_jefe(page):
    """Inicia sesión como Jefe y verifica que no haya redirección inesperada."""
    page.goto(f"{BASE_URL}/Cuenta/Logout")
    page.wait_for_load_state("networkidle")
    hacer_login(page, CORREO_JEFE, PASSWORD)
    if "/Cuenta/CambiarPassword" in page.url:
        pytest.skip("Redirigido a CambiarPassword — estado de BD inesperado.")


def _ir_a_perfil_carlos(page):
    """Navega al perfil del Jefe (Carlos) directamente desde /Empleado."""
    _login_jefe(page)
    page.goto(f"{BASE_URL}/Empleado")
    page.wait_for_load_state("networkidle")
    # El Jefe puede ver su propio perfil; lo buscamos por nombre en la tabla
    link = page.locator("a.table-link", has_text="Carlos Alberto Rodríguez Mora")
    link.first.click()
    page.wait_for_load_state("networkidle")


def _ir_a_historial(page):
    """Navega al perfil de Carlos y abre el tab Historial."""
    _ir_a_perfil_carlos(page)
    page.locator("a[role='tab']", has_text="Historial").click()
    page.wait_for_load_state("networkidle")
    # Asegurarnos de que la tabla de eventos cargó
    page.wait_for_selector("input[name='desde']", timeout=8000)


def _obtener_id_valentina(page) -> str:
    """Obtiene el ID de Valentina Ospina (empleada inactiva con FechaInicioContrato)."""
    page.goto(f"{BASE_URL}/Empleado?estado=Inactivo")
    page.wait_for_load_state("networkidle")
    link = page.locator("a.table-link", has_text="Valentina Ospina Restrepo")
    href = link.first.get_attribute("href")
    # href es algo como /Empleado/Perfil/10 — extraemos el ID
    emp_id = href.split("/")[-1]
    return emp_id


# ─── Fixture ─────────────────────────────────────────────────────────────────

@pytest.fixture(autouse=True)
def login_jefe(page):
    """Login del Jefe antes de cada test."""
    _login_jefe(page)


# ── TC-VAC-01 ─────────────────────────────────────────────────────────────────
def test_tc_vac01_columna_dias_visible(page):
    """La columna 'Días' debe existir en la tabla del tab Historial."""
    _ir_a_historial(page)

    encabezados = page.locator("table thead th").all_text_contents()
    assert "Días" in encabezados, (
        f"TC-VAC-01 FALLO: Columna 'Días' no encontrada. Encabezados: {encabezados}"
    )
    print(f"\n  TC-VAC-01 PASO - Encabezados: {encabezados}")


# ── TC-VAC-02 ─────────────────────────────────────────────────────────────────
def test_tc_vac02_valor_dias_correcto(page):
    """
    Vacaciones Carlos dic 2024: 2024-12-23 -> 2025-01-05 = 14 dias
    Vacaciones Carlos dic 2025: 2025-12-22 -> 2026-01-04 = 14 dias
    Al menos una fila debe mostrar 14 en la columna Dias.
    """
    _ir_a_historial(page)

    # Apuntar solo a la tabla de eventos (la que tiene columna "Autorizado por")
    tabla_eventos = page.locator("table:has(th:has-text('Autorizado'))")
    headers = tabla_eventos.locator("thead th").all_text_contents()
    idx_dias = next((i for i, h in enumerate(headers) if "D" in h and "as" in h), None)
    assert idx_dias is not None, f"TC-VAC-02 FALLO: Columna 'Dias' no encontrada. Headers: {headers}"

    filas = tabla_eventos.locator("tbody tr").all()
    valores_dias = []
    for fila in filas:
        celdas = fila.locator("td").all_text_contents()
        if len(celdas) > idx_dias:
            valores_dias.append(celdas[idx_dias].strip())

    assert "14" in valores_dias, (
        f"TC-VAC-02 FALLO: Ninguna fila muestra 14 dias. Valores: {valores_dias}"
    )
    print(f"\n  TC-VAC-02 PASO - Valores de dias encontrados: {valores_dias}")


# ── TC-VAC-03 ─────────────────────────────────────────────────────────────────
def test_tc_vac03_filtros_visibles(page):
    """Los inputs 'desde' y 'hasta' deben existir en el tab Historial."""
    _ir_a_historial(page)

    assert page.is_visible("input[name='desde']"), (
        "TC-VAC-03 FALLO: Input 'desde' no visible."
    )
    assert page.is_visible("input[name='hasta']"), (
        "TC-VAC-03 FALLO: Input 'hasta' no visible."
    )
    print("\n  TC-VAC-03 PASO - Filtros Desde/Hasta visibles.")


# ── TC-VAC-04 ─────────────────────────────────────────────────────────────────
def test_tc_vac04_filtro_rango_filtra(page):
    """
    Filtrar por 2025-12-01 → 2026-01-31 debe mostrar solo las vacaciones de dic 2025
    (FechaInicio 2025-12-22) y NO las de dic 2024 (FechaInicio 2024-12-23).
    """
    _ir_a_historial(page)

    page.fill("input[name='desde']", "2025-12-01")
    page.fill("input[name='hasta']", "2026-01-31")
    page.locator("button[type='submit']:has-text('Filtrar')").click()
    page.wait_for_load_state("networkidle")

    # Debe haber al menos una fila (vacaciones 2025-12-22)
    filas = page.locator("table tbody tr").all()
    assert len(filas) >= 1, "TC-VAC-04 FALLO: No hay filas tras aplicar filtro."

    # Apuntar solo al tbody de la tabla de eventos para evitar strict mode (3 tbodies en el tab)
    # La tabla de eventos es la que contiene la columna "Autorizado por"
    texto_tabla = page.locator("table:has(th:has-text('Autorizado')) tbody").inner_text()

    # Ninguna fila debe contener "23/12/2024"
    assert "23/12/2024" not in texto_tabla, (
        "TC-VAC-04 FALLO: La fila de dic 2024 aparecio fuera del rango filtrado."
    )
    # La fila de 2025-12-22 SI debe estar (formato dd/MM/yyyy en la tabla)
    assert "22/12/2025" in texto_tabla, (
        "TC-VAC-04 FALLO: La fila de dic 2025 no aparece en el rango filtrado."
    )
    print(f"\n  TC-VAC-04 PASO - {len(filas)} evento(s) dentro del rango 2025-12-01 / 2026-01-31.")


# ── TC-VAC-05 ─────────────────────────────────────────────────────────────────
def test_tc_vac05_filtro_sin_resultados(page):
    """Filtrar por un rango futuro sin eventos debe mostrar estado vacío."""
    _ir_a_historial(page)

    page.fill("input[name='desde']", "2030-01-01")
    page.fill("input[name='hasta']", "2030-12-31")
    page.locator("button[type='submit']:has-text('Filtrar')").click()
    page.wait_for_load_state("networkidle")

    empty_state = page.locator(".empty-state")
    assert empty_state.is_visible(), (
        "TC-VAC-05 FALLO: El estado vacío no se muestra con rango sin eventos."
    )
    print("\n  TC-VAC-05 PASO - Estado vacío visible con rango futuro sin eventos.")


# ── TC-VAC-06 ─────────────────────────────────────────────────────────────────
def test_tc_vac06_boton_limpiar_restaura(page):
    """Después de filtrar, 'Limpiar' debe mostrar todos los eventos originales."""
    _ir_a_historial(page)

    # Contar filas sin filtro
    filas_sin_filtro = len(page.locator("table tbody tr").all())

    # Aplicar filtro restrictivo
    page.fill("input[name='desde']", "2025-12-01")
    page.fill("input[name='hasta']", "2026-01-31")
    page.locator("button[type='submit']:has-text('Filtrar')").click()
    page.wait_for_load_state("networkidle")

    filas_filtradas = len(page.locator("table tbody tr").all())

    # Limpiar
    page.locator("a:has-text('Limpiar')").click()
    page.wait_for_load_state("networkidle")

    filas_limpiadas = len(page.locator("table tbody tr").all())

    assert filas_limpiadas == filas_sin_filtro, (
        f"TC-VAC-06 FALLO: Después de limpiar hay {filas_limpiadas} filas, "
        f"pero originalmente había {filas_sin_filtro}."
    )
    assert filas_filtradas < filas_sin_filtro or filas_sin_filtro == 0, (
        "TC-VAC-06 AVISO: El filtro no redujo la cantidad de filas (datos insuficientes)."
    )
    print(f"\n  TC-VAC-06 PASO - {filas_sin_filtro} -> {filas_filtradas} -> {filas_limpiadas} filas.")


# ── TC-VAC-07 ─────────────────────────────────────────────────────────────────
def test_tc_vac07_resumen_visible(page):
    """El resumen por tipo de evento debe ser visible cuando hay eventos."""
    _ir_a_historial(page)

    # La tabla de resumen está antes de la tabla principal y tiene encabezado "Tipo de evento"
    resumen = page.locator("table:has(th:has-text('Tipo de evento'))")
    assert resumen.is_visible(), (
        "TC-VAC-07 FALLO: La tabla de resumen no es visible."
    )
    filas_resumen = resumen.locator("tbody tr").all()
    assert len(filas_resumen) >= 1, (
        "TC-VAC-07 FALLO: La tabla de resumen está vacía (no tiene filas de tipo)."
    )
    tipos = [f.locator("td").first.inner_text().strip() for f in filas_resumen]
    print(f"\n  TC-VAC-07 PASO - Tipos en resumen: {tipos}")


# ── TC-VAC-08 ─────────────────────────────────────────────────────────────────
def test_tc_vac08_resumen_cambia_al_filtrar(page):
    """
    Filtrar por 2025-12-01 → 2026-01-31 debe cambiar los totales del resumen.
    Sin filtro Carlos tiene 2 vacaciones (28 días total).
    Con filtro solo 1 vacación (14 días).
    """
    _ir_a_historial(page)

    # Resumen sin filtro
    resumen_sin_filtro = page.locator("table:has(th:has-text('Tipo de evento'))")
    filas_sf = resumen_sin_filtro.locator("tbody tr").all()
    # Buscar la fila de Vacaciones y su total
    total_sin_filtro = None
    for fila in filas_sf:
        celdas = fila.locator("td").all_text_contents()
        if celdas and "Vacaciones" in celdas[0]:
            total_sin_filtro = celdas[1].strip()
            break

    # Aplicar filtro
    page.fill("input[name='desde']", "2025-12-01")
    page.fill("input[name='hasta']", "2026-01-31")
    page.locator("button[type='submit']:has-text('Filtrar')").click()
    page.wait_for_load_state("networkidle")

    resumen_con_filtro = page.locator("table:has(th:has-text('Tipo de evento'))")
    filas_cf = resumen_con_filtro.locator("tbody tr").all()
    total_con_filtro = None
    for fila in filas_cf:
        celdas = fila.locator("td").all_text_contents()
        if celdas and "Vacaciones" in celdas[0]:
            total_con_filtro = celdas[1].strip()
            break

    # Con filtro debe haber exactamente 14 días (1 evento de vacaciones)
    assert total_con_filtro == "14", (
        f"TC-VAC-08 FALLO: Se esperaban 14 días de vacaciones con filtro, "
        f"se obtuvo: {total_con_filtro!r}."
    )
    print(
        f"\n  TC-VAC-08 PASO - Total vacaciones sin filtro: {total_sin_filtro}, "
        f"con filtro dic-2025/ene-2026: {total_con_filtro}."
    )


# ── TC-VAC-09 ─────────────────────────────────────────────────────────────────
def test_tc_vac09_vacaciones_disponibles_con_valor(page):
    """
    Valentina Ospina (inactiva) tiene FechaInicioContrato='2024-01-15'.
    El campo 'Vacaciones disponibles' debe mostrar un valor numérico con 'días'.
    """
    emp_id = _obtener_id_valentina(page)
    page.goto(f"{BASE_URL}/Empleado/Perfil/{emp_id}?tab=datos")
    page.wait_for_load_state("networkidle")

    # Buscar el dl-item que contiene "Vacaciones disponibles"
    label = page.locator("p.dl-label", has_text="Vacaciones disponibles")
    assert label.is_visible(), (
        "TC-VAC-09 FALLO: Label 'Vacaciones disponibles' no encontrado en tab Datos."
    )

    valor_elem = label.locator("xpath=following-sibling::p[@class='dl-value']")
    valor_texto = valor_elem.inner_text().strip()

    assert "días" in valor_texto.lower(), (
        f"TC-VAC-09 FALLO: El valor no contiene 'días': {valor_texto!r}."
    )
    assert valor_texto != "—", (
        f"TC-VAC-09 FALLO: El valor es '—', se esperaba un número de días."
    )
    print(f"\n  TC-VAC-09 PASO - Vacaciones disponibles: {valor_texto}")


# ── TC-VAC-10 ─────────────────────────────────────────────────────────────────
def test_tc_vac10_vacaciones_disponibles_vacio(page):
    """
    Carlos Rodríguez (FechaInicioContrato=NULL) debe mostrar '—' en Vacaciones disponibles.
    """
    _ir_a_perfil_carlos(page)
    # Asegurarse de estar en tab datos (por defecto)
    if "tab=historial" in page.url or "tab=horario" in page.url:
        page.goto(page.url.replace("tab=historial", "tab=datos").replace("tab=horario", "tab=datos"))
        page.wait_for_load_state("networkidle")

    label = page.locator("p.dl-label", has_text="Vacaciones disponibles")
    assert label.is_visible(), (
        "TC-VAC-10 FALLO: Label 'Vacaciones disponibles' no encontrado en tab Datos."
    )

    valor_elem = label.locator("xpath=following-sibling::p[@class='dl-value']")
    valor_texto = valor_elem.inner_text().strip()

    assert valor_texto == "—", (
        f"TC-VAC-10 FALLO: Se esperaba '—' para empleado sin FechaInicioContrato, "
        f"se obtuvo: {valor_texto!r}."
    )
    print(f"\n  TC-VAC-10 PASO - Vacaciones disponibles muestra: {valor_texto!r}")
