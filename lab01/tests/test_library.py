"""Basic tests for the Library system — validates existing methods work."""

import pytest
from datetime import date, timedelta
from library import Library, Book, Member, Genre, Loan


@pytest.fixture
def library():
    lib = Library()
    lib.add_book(Book("978-1", "Python Basics", "Alice Smith", Genre.TECHNOLOGY, 2021, copies_total=2, copies_available=2))
    lib.add_book(Book("978-2", "Mystery Novel", "Bob Jones", Genre.MYSTERY, 2019))
    lib.register_member(Member("M001", "Charlie", "charlie@example.com"))
    lib.register_member(Member("M002", "Dana", "dana@example.com"))
    return lib


class TestBookManagement:
    def test_add_and_get_book(self, library):
        book = library.get_book("978-1")
        assert book is not None
        assert book.title == "Python Basics"

    def test_get_book_not_found(self, library):
        assert library.get_book("000") is None

    def test_search_books_by_title(self, library):
        results = library.search_books("python")
        assert len(results) == 1
        assert results[0].isbn == "978-1"

    def test_search_books_by_author(self, library):
        results = library.search_books("bob")
        assert len(results) == 1
        assert results[0].isbn == "978-2"

    def test_search_books_no_match(self, library):
        assert library.search_books("nonexistent") == []


class TestCheckout:
    def test_checkout_success(self, library):
        result = library.checkout_book("978-1", "M001")
        assert result["status"] == "ok"
        assert "loan_id" in result
        assert library.get_book("978-1").copies_available == 1

    def test_checkout_unknown_book(self, library):
        result = library.checkout_book("000", "M001")
        assert result["status"] == "error"

    def test_checkout_unknown_member(self, library):
        result = library.checkout_book("978-1", "UNKNOWN")
        assert result["status"] == "error"

    def test_checkout_no_copies(self, library):
        library.checkout_book("978-2", "M001")  # only 1 copy
        result = library.checkout_book("978-2", "M002")
        assert result["status"] == "error"
        assert "No copies" in result["message"]

    def test_checkout_inactive_member(self, library):
        library.get_member("M002").is_active = False
        result = library.checkout_book("978-1", "M002")
        assert result["status"] == "error"
        assert "inactive" in result["message"].lower()


class TestReturn:
    def test_return_success(self, library):
        checkout = library.checkout_book("978-1", "M001")
        result = library.return_book(checkout["loan_id"])
        assert result["status"] == "ok"
        assert result["was_overdue"] is False
        assert library.get_book("978-1").copies_available == 2

    def test_return_not_found(self, library):
        result = library.return_book("LOAN-999999")
        assert result["status"] == "error"

    def test_return_overdue(self, library):
        checkout = library.checkout_book("978-1", "M001")
        # Manually set due_date in the past to simulate overdue
        loan = library._loans[-1]
        loan.due_date = date.today() - timedelta(days=1)
        result = library.return_book(checkout["loan_id"])
        assert result["status"] == "ok"
        assert result["was_overdue"] is True


# ══════════════════════════════════════════════════════════════════
# TODO verification tests — these cover the 9 methods participants
# must implement.  They are marked xfail so the suite stays green
# until the TODOs are completed.
# ══════════════════════════════════════════════════════════════════

class TestSearchByGenre:
    @pytest.mark.xfail(reason="TODO: implement search_by_genre in library.py")
    def test_search_by_genre_returns_matches(self, library):
        results = library.search_by_genre(Genre.TECHNOLOGY)
        assert len(results) == 1
        assert results[0].isbn == "978-1"

    @pytest.mark.xfail(reason="TODO: implement search_by_genre in library.py")
    def test_search_by_genre_no_match(self, library):
        results = library.search_by_genre(Genre.FANTASY)
        assert results == []


class TestGetAvailableBooks:
    @pytest.mark.xfail(reason="TODO: implement get_available_books in library.py")
    def test_all_available_initially(self, library):
        available = library.get_available_books()
        assert len(available) == 2

    @pytest.mark.xfail(reason="TODO: implement get_available_books in library.py")
    def test_excludes_fully_checked_out(self, library):
        library.checkout_book("978-2", "M001")  # only 1 copy
        available = library.get_available_books()
        assert all(b.isbn != "978-2" for b in available)


class TestGetMostPopularBooks:
    @pytest.mark.xfail(reason="TODO: implement get_most_popular_books in library.py")
    def test_most_popular_ordered_by_loans(self, library):
        library.checkout_book("978-1", "M001")
        library.checkout_book("978-1", "M002")
        library.checkout_book("978-2", "M001")
        popular = library.get_most_popular_books()
        assert popular[0].isbn == "978-1"  # 2 loans vs 1


class TestDeactivateMember:
    @pytest.mark.xfail(reason="TODO: implement deactivate_member in library.py")
    def test_deactivate_sets_inactive(self, library):
        library.deactivate_member("M001")
        assert library.get_member("M001").is_active is False

    @pytest.mark.xfail(reason="TODO: implement deactivate_member in library.py")
    def test_deactivate_unknown_member(self, library):
        result = library.deactivate_member("UNKNOWN")
        # Should signal an error (None, False, or raise — any is fine)
        assert result is None or result is False or result == {"status": "error"}


class TestSearchMembers:
    @pytest.mark.xfail(reason="TODO: implement search_members in library.py")
    def test_search_members_by_name(self, library):
        results = library.search_members("char")
        assert len(results) == 1
        assert results[0].member_id == "M001"

    @pytest.mark.xfail(reason="TODO: implement search_members in library.py")
    def test_search_members_no_match(self, library):
        assert library.search_members("zzz") == []


class TestGetOverdueLoans:
    @pytest.mark.xfail(reason="TODO: implement get_overdue_loans in library.py")
    def test_overdue_loans_returned(self, library):
        library.checkout_book("978-1", "M001")
        library._loans[-1].due_date = date.today() - timedelta(days=1)
        overdue = library.get_overdue_loans()
        assert len(overdue) == 1
        assert overdue[0].member_id == "M001"


class TestExtendLoan:
    @pytest.mark.xfail(reason="TODO: implement extend_loan in library.py")
    def test_extend_loan_adds_days(self, library):
        checkout = library.checkout_book("978-1", "M001")
        original_due = library._loans[-1].due_date
        library.extend_loan(checkout["loan_id"], 7)
        assert library._loans[-1].due_date == original_due + timedelta(days=7)


class TestGetMemberLoanHistory:
    @pytest.mark.xfail(reason="TODO: implement get_member_loan_history in library.py")
    def test_member_loan_history(self, library):
        library.checkout_book("978-1", "M001")
        library.checkout_book("978-2", "M001")
        history = library.get_member_loan_history("M001")
        assert len(history) == 2


class TestLibrarySummary:
    @pytest.mark.xfail(reason="TODO: implement summary/report method in library.py")
    def test_summary_keys(self, library):
        library.checkout_book("978-1", "M001")
        summary = library.get_summary()
        assert summary["total_books"] == 2
        assert summary["total_members"] == 2
        assert summary["active_loans"] == 1
        assert summary["overdue_loans"] == 0
