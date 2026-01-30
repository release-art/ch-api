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

    def test_links_section_get_link_from_pydantic_extra(self):
        """Test get_link accesses __pydantic_extra__ directly (line 163)."""
        # Create a LinksSection with extra fields that are stored in __pydantic_extra__
        data = {
            "dynamic_link": "https://api.example.com/dynamic",
            "resource_url": "https://api.example.com/resource",
        }

        links = shared.LinksSection.model_validate(data)

        # Both extra fields should be retrievable via get_link
        assert links.get_link("dynamic_link") == "https://api.example.com/dynamic"
        assert links.get_link("resource_url") == "https://api.example.com/resource"
        
        # Verify that __pydantic_extra__ is being used (line 163 uses it)
        assert links.__pydantic_extra__ is not None
        assert "dynamic_link" in links.__pydantic_extra__

    def test_links_section_get_link_returns_from_pydantic_extra(self):
        """Test that get_link correctly returns values from __pydantic_extra__ (line 163)."""
        # Create a LinksSection with only extra fields (no declared fields)
        data = {
            "undeclared_link": "https://api.example.com/undeclared",
            "another_custom": "https://api.example.com/custom",
        }

        links = shared.LinksSection.model_validate(data)

        # Get a link from __pydantic_extra__
        result = links.get_link("undeclared_link")

        # This should execute line 163: return self.__pydantic_extra__.get(name, None)
        assert result == "https://api.example.com/undeclared"
        assert links.get_link("another_custom") == "https://api.example.com/custom"

    def test_links_section_get_link_with_extra_none(self):
        """Test get_link when __pydantic_extra__ is explicitly None (line 162-163)."""
        # Create a LinksSection and manually set __pydantic_extra__ to None
        links = shared.LinksSection.model_validate({})
        
        # Manually set __pydantic_extra__ to None to test the None check
        links.__pydantic_extra__ = None
        
        # This should return None due to the check on line 162
        result = links.get_link("any_link")
        assert result is None
