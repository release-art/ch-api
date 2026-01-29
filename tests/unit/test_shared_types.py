"""Unit tests for shared data types."""

from ch_api.types import shared


class TestLinksSection:
    """Test LinksSection model."""

    def test_links_section_with_self_link(self):
        """Test LinksSection with self link."""
        data = {"self": "https://api.company-information.service.gov.uk/company/09370755"}

        links = shared.LinksSection.model_validate(data)

        assert links.self == "https://api.company-information.service.gov.uk/company/09370755"

    def test_links_section_get_link_self(self):
        """Test get_link method for self link."""
        data = {"self": "https://api.example.com/resource"}

        links = shared.LinksSection.model_validate(data)
        result = links.get_link("self")

        assert result == "https://api.example.com/resource"

    def test_links_section_get_link_custom(self):
        """Test get_link method for custom link."""
        data = {
            "self": "https://api.example.com/resource",
            "company": "https://api.example.com/company/123",
        }

        links = shared.LinksSection.model_validate(data)
        result = links.get_link("company")

        assert result == "https://api.example.com/company/123"

    def test_links_section_get_link_missing(self):
        """Test get_link returns None for missing link."""
        data = {"self": "https://api.example.com/resource"}

        links = shared.LinksSection.model_validate(data)
        result = links.get_link("nonexistent")

        assert result is None

    def test_links_section_self_property_missing(self):
        """Test self property returns None when self link missing."""
        data = {"company": "https://api.example.com/company/123"}

        links = shared.LinksSection.model_validate(data)

        assert links.self is None

    def test_links_section_empty(self):
        """Test LinksSection with no links."""
        data = {}

        links = shared.LinksSection.model_validate(data)

        assert links.self is None
        assert links.get_link("any") is None

    def test_links_section_multiple_links(self):
        """Test LinksSection with multiple links."""
        data = {
            "self": "https://api.example.com/resource",
            "company": "https://api.example.com/company/456",
            "officer": "https://api.example.com/officer/789",
            "appointments": "https://api.example.com/appointments",
        }

        links = shared.LinksSection.model_validate(data)

        assert links.self == "https://api.example.com/resource"
        assert links.get_link("company") == "https://api.example.com/company/456"
        assert links.get_link("officer") == "https://api.example.com/officer/789"
        assert links.get_link("appointments") == "https://api.example.com/appointments"

    def test_links_section_extra_fields_allowed(self):
        """Test that LinksSection allows extra fields."""
        data = {
            "self": "https://api.example.com/resource",
            "custom_link": "https://api.example.com/custom",
            "another_field": "value",
        }

        links = shared.LinksSection.model_validate(data)

        # Should not raise and should have the extra fields
        assert links.get_link("custom_link") == "https://api.example.com/custom"
        assert links.get_link("another_field") == "value"
