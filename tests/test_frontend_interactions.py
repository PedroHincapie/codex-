import unittest
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parents[1]
INDEX = (ROOT_DIR / "frontend" / "index.html").read_text(encoding="utf-8")
APP = (ROOT_DIR / "frontend" / "app.js").read_text(encoding="utf-8")


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


if __name__ == "__main__":
  unittest.main()
