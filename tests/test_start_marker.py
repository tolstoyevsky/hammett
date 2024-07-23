"""The module contains the tests for the StartMarker."""

from hammett.start_marker import StartMarker
from hammett.test.base import BaseTestCase

_BOOK_ID = '1'

_EXTRA_VALUE = 'extra_value'

_SOURCE = 'inbio'


class StartMarkerTests(BaseTestCase):
    """The class implements the tests for the StartMarker."""

    def test_getting_more_than_one_start_marker(self):
        """Test getting more than one start marker."""
        start_marker = StartMarker(f'/start {_SOURCE}=book={_BOOK_ID}')
        book_id = start_marker['book']
        source = start_marker['source']

        self.assertEqual(book_id, _BOOK_ID)
        self.assertEqual(source, _SOURCE)

    def test_getting_start_marker_which_is_not_source(self):
        """Test getting a start-marker which is not a source."""
        start_marker = StartMarker(f'/start book={_BOOK_ID}')
        book_id = start_marker['book']

        self.assertEqual(book_id, _BOOK_ID)

    def test_getting_only_one_start_marker_ignoring_others(self):
        """Test getting only one start-marker ignoring others."""
        start_marker = StartMarker(f'/start {_SOURCE}=book={_BOOK_ID}=extra={_EXTRA_VALUE}')
        extra = start_marker['extra']

        self.assertEqual(extra, _EXTRA_VALUE)

    def test_getting_start_marker_which_is_source(self):
        """Test getting a start-marker which is a source."""
        start_marker = StartMarker(f'/start {_SOURCE}')
        source = start_marker['source']

        self.assertEqual(source, _SOURCE)

    def test_getting_start_markers_without_any_markers(self):
        """Test getting start-markers without any markers."""
        start_marker = StartMarker('/start ')

        with self.assertRaises(KeyError):
            start_marker['source']
