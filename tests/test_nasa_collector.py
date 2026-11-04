import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts" / "collectors"))

from nasa import map_nasa_item, map_nasa_response


class NasaCollectorTests(unittest.TestCase):
    def make_item(self, nasa_id="NHQ_2024_0101", title="NASA test asset",
                  media_type="image", links=None, extra=None):
        metadata = {
            "nasa_id": nasa_id,
            "title": title,
            "media_type": media_type,
            "photographer": "NASA/Example Photographer",
            "description": "  Example   description  ",
        }
        metadata.update(extra or {})
        return {"data": [metadata], "links": links or []}

    def test_maps_image_and_normalizes_metadata(self):
        item = self.make_item(
            media_type="image",
            links=[{"rel": "preview", "href": "https://images.example/thumb.jpg"}],
        )

        record = map_nasa_item(item)

        self.assertIsNotNone(record)
        self.assertEqual(record["media_type"], "image")
        self.assertEqual(record["source"], "nasa_nail")
        self.assertEqual(record["source_id"], "NHQ_2024_0101")
        self.assertEqual(record["title"], "NASA test asset")
        self.assertEqual(record["creator"], "NASA/Example Photographer")
        self.assertEqual(record["description"], "Example description")
        self.assertEqual(record["thumbnail_url"], "https://images.example/thumb.jpg")
        self.assertEqual(record["source_url"], "https://images.nasa.gov/details/NHQ_2024_0101")

    def test_maps_video_as_video_without_inventing_duration_or_media_url(self):
        record = map_nasa_item(self.make_item(media_type="video"))

        self.assertIsNotNone(record)
        self.assertEqual(record["media_type"], "video")
        self.assertIsNone(record["duration_seconds"])
        self.assertIsNone(record["media_url"])

    def test_incomplete_records_are_rejected(self):
        self.assertIsNone(map_nasa_item({}))
        self.assertIsNone(map_nasa_item({"data": []}))
        self.assertIsNone(map_nasa_item(self.make_item(title="   ")))
        self.assertIsNone(map_nasa_item(self.make_item(nasa_id="")))

    def test_missing_identification_is_not_replaced_with_guessed_values(self):
        missing_id = self.make_item(nasa_id=None)
        missing_title = self.make_item(title=None)

        self.assertIsNone(map_nasa_item(missing_id))
        self.assertIsNone(map_nasa_item(missing_title))

    def test_unknown_media_type_stays_unknown(self):
        record = map_nasa_item(self.make_item(media_type="document"))

        self.assertEqual(record["media_type"], "unknown")

    def test_preview_must_use_https(self):
        item = self.make_item(
            links=[
                {"rel": "preview", "href": "http://images.example/thumb.jpg"},
                {"rel": "preview", "href": "https://images.example/secure.jpg"},
            ]
        )

        record = map_nasa_item(item)

        self.assertEqual(record["thumbnail_url"], "https://images.example/secure.jpg")

    def test_every_item_requires_individual_rights_review(self):
        record = map_nasa_item(self.make_item())

        self.assertEqual(record["rights_status"], "review_required")
        self.assertIn("item-specific", record["rights_evidence"])
        self.assertIsNone(record["license"])
        self.assertIsNone(record["license_url"])

    def test_response_mapper_skips_invalid_items_and_maps_valid_items(self):
        response = {
            "collection": {
                "items": [
                    self.make_item(media_type="image"),
                    self.make_item(nasa_id="VIDEO_02", media_type="video"),
                    {"data": [{"title": "No NASA ID"}]},
                    "not-an-item",
                ]
            }
        }

        records = map_nasa_response(response)

        self.assertEqual(len(records), 2)
        self.assertEqual([r["media_type"] for r in records], ["image", "video"])
        self.assertTrue(all(r["rights_status"] == "review_required" for r in records))

    def test_empty_or_missing_collection_returns_empty_list(self):
        self.assertEqual(map_nasa_response({}), [])
        self.assertEqual(map_nasa_response({"collection": {"items": []}}), [])


if __name__ == "__main__":
    unittest.main()
