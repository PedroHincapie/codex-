import unittest
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parents[1]
INDEX = (ROOT_DIR / "frontend" / "index.html").read_text(encoding="utf-8")
APP = (ROOT_DIR / "frontend" / "app.js").read_text(encoding="utf-8")
STYLES = (ROOT_DIR / "frontend" / "styles.css").read_text(encoding="utf-8")
GLOSSARY = (ROOT_DIR / "docs" / "ai-radar-ui-glossary.md").read_text(encoding="utf-8")


class FrontendInteractionsTest(unittest.TestCase):
  def test_all_sidebar_sections_have_declared_views(self):
    for view in ("radar", "rankings", "sources", "evidence", "reviews"):
      self.assertIn(f'data-view="{view}"', INDEX)
      self.assertIn(f"{view}:", APP)
    self.assertIn('aria-current="page"', INDEX)
    self.assertIn("setActiveView", APP)

  def test_notifications_have_accessible_dialog_and_real_state(self):
    self.assertIn('aria-controls="notification-panel"', INDEX)
    self.assertIn('role="dialog"', INDEX)
    self.assertIn("buildNotifications", APP)
    self.assertIn("Notificaciones, sin pendientes", APP)
    self.assertIn("Marcar como revisadas", APP)

  def test_escape_closes_navigation_and_notifications(self):
    self.assertIn('event.key === "Escape"', APP)
    self.assertIn("toggleNotifications(false)", APP)
    self.assertIn('elements.sidebar.classList.remove("is-open")', APP)

  def test_reader_and_operator_have_distinct_spanish_navigation(self):
    self.assertIn('data-mode-nav="reader"', INDEX)
    self.assertIn('data-mode-nav="operator"', INDEX)
    self.assertIn("Explorar", INDEX)
    self.assertIn("Revisar", INDEX)
    self.assertIn("modeMetadata[mode].defaultView", APP)
    self.assertIn("Ranking de señales", INDEX)
    self.assertIn("Puntuación editorial", INDEX)
    self.assertIn("Confianza editorial", GLOSSARY)

  def test_responsive_evidence_drawer_has_focus_and_backdrop_controls(self):
    self.assertIn('id="evidence-backdrop"', INDEX)
    self.assertIn("syncEvidencePresentation", APP)
    self.assertIn('setAttribute("aria-modal", "true")', APP)
    self.assertIn('event.key === "Tab"', APP)
    self.assertIn(".evidence-backdrop", STYLES)
    self.assertIn("100dvh", STYLES)

  def test_long_sections_have_search_pagination_and_explicit_counts(self):
    for view in ("sources", "evidence", "reviews"):
      self.assertIn(f'{view}:', APP)
      self.assertIn(f'renderSectionSearch("{view}"', APP)
    self.assertIn("Mostrando ${first}–${pageData.end} de ${pageData.total}", APP)
    self.assertIn('id="mobile-last-updated"', INDEX)


if __name__ == "__main__":
  unittest.main()
