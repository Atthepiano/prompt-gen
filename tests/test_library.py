"""测试 core.library。每个 case 用独立 tmp 目录的 SQLite，互不影响。"""
import os
import tempfile
import unittest

from core import library


class LibraryTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        library.configure(os.path.join(self.tmp.name, "test.db"))

    def tearDown(self):
        library.reset_for_test()
        self.tmp.cleanup()

    # --- add / get ---

    def test_add_and_get_round_trip(self):
        rid = library.add_entry(
            generator_type="character",
            params={"gender": "Female", "age": 25},
            prompt="some prompt text",
            image_path="C:/fake/path.png",
            tags=["wip", "good-pose"],
            rating=4,
            notes="试试看",
        )
        self.assertIsNotNone(rid)
        entry = library.get_entry(rid)
        self.assertIsNotNone(entry)
        self.assertEqual(entry.generator_type, "character")
        self.assertEqual(entry.params, {"gender": "Female", "age": 25})
        self.assertEqual(entry.prompt, "some prompt text")
        self.assertEqual(entry.rating, 4)
        self.assertEqual(set(entry.tags), {"wip", "good-pose"})
        self.assertEqual(entry.notes, "试试看")

    def test_get_missing_returns_none(self):
        self.assertIsNone(library.get_entry(999999))

    # --- list / filter ---

    def test_list_orders_by_created_desc(self):
        for i in range(3):
            library.add_entry(generator_type="spaceship", prompt=f"p{i}", image_path=f"img{i}.png")
        rows = library.list_entries()
        self.assertEqual(len(rows), 3)
        # 最新插入的应在最前
        self.assertEqual(rows[0].prompt, "p2")
        self.assertEqual(rows[-1].prompt, "p0")

    def test_filter_by_generator_type(self):
        library.add_entry(generator_type="character", prompt="a")
        library.add_entry(generator_type="clothing", prompt="b")
        library.add_entry(generator_type="character", prompt="c")
        rows = library.list_entries(generator_type="character")
        self.assertEqual(len(rows), 2)
        self.assertTrue(all(r.generator_type == "character" for r in rows))

    def test_filter_by_min_rating(self):
        library.add_entry(generator_type="x", prompt="low", rating=1)
        rid = library.add_entry(generator_type="x", prompt="high", rating=5)
        rows = library.list_entries(min_rating=3)
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0].id, rid)

    def test_filter_by_tag(self):
        library.add_entry(generator_type="x", prompt="a", tags=["hero"])
        library.add_entry(generator_type="x", prompt="b", tags=["villain"])
        library.add_entry(generator_type="x", prompt="c", tags=["hero", "wip"])
        rows = library.list_entries(tag="hero")
        self.assertEqual(len(rows), 2)
        self.assertEqual({r.prompt for r in rows}, {"a", "c"})

    def test_filter_by_keyword_matches_prompt_or_notes_or_tag(self):
        library.add_entry(generator_type="x", prompt="rocket launcher", notes="")
        library.add_entry(generator_type="x", prompt="laser cannon", notes="for hero")
        library.add_entry(generator_type="x", prompt="shield", tags=["heroic"])
        rows = library.list_entries(keyword="hero")
        self.assertEqual(len(rows), 2)

    # --- update ---

    def test_update_rating_clamps_to_0_5(self):
        rid = library.add_entry(generator_type="x", prompt="a")
        library.update_rating(rid, 99)
        self.assertEqual(library.get_entry(rid).rating, 5)
        library.update_rating(rid, -3)
        self.assertEqual(library.get_entry(rid).rating, 0)

    def test_update_tags_strips_whitespace_and_empty(self):
        rid = library.add_entry(generator_type="x", prompt="a")
        library.update_tags(rid, [" hero ", "", "wip"])
        self.assertEqual(set(library.get_entry(rid).tags), {"hero", "wip"})

    def test_update_notes(self):
        rid = library.add_entry(generator_type="x", prompt="a")
        library.update_notes(rid, "记一笔")
        self.assertEqual(library.get_entry(rid).notes, "记一笔")

    # --- delete / count / tags ---

    def test_delete(self):
        rid = library.add_entry(generator_type="x", prompt="a")
        self.assertTrue(library.delete_entry(rid))
        self.assertIsNone(library.get_entry(rid))

    def test_count(self):
        for _ in range(3):
            library.add_entry(generator_type="character", prompt="x")
        for _ in range(2):
            library.add_entry(generator_type="clothing", prompt="y")
        self.assertEqual(library.count(), 5)
        self.assertEqual(library.count("character"), 3)
        self.assertEqual(library.count("clothing"), 2)
        self.assertEqual(library.count("nonexistent"), 0)

    def test_all_tags_dedup_and_sorted(self):
        library.add_entry(generator_type="x", prompt="a", tags=["b", "a"])
        library.add_entry(generator_type="x", prompt="c", tags=["a", "c"])
        self.assertEqual(library.all_tags(), ["a", "b", "c"])

    def test_add_with_no_optional_fields(self):
        """生成器只传必填项也应能成功。"""
        rid = library.add_entry(generator_type="slicer")
        self.assertIsNotNone(rid)
        e = library.get_entry(rid)
        self.assertEqual(e.params, {})
        self.assertEqual(e.tags, [])
        self.assertEqual(e.rating, 0)


if __name__ == "__main__":
    unittest.main()
