from pydantic import BaseModel, Field

class SchemaPartSelect(BaseModel):
    appliance_type: str = Field(description="The type of appliance it works for")
    part_name: str = Field(description="The name of the part")
    partselect_number: str = Field(description="The partselect number of the part")
    manufacturer_part_number: str = Field(description="The manufacturer part number of the part")
    manufacturer_name: str = Field(description="The manufacturer name of the part")
    manufactured_for: str = Field(description="The manufactured for of the part")
    product_description: str = Field(description="The product description of the part")
    symptoms_fixed: str = Field(description="The symptoms fixed by the part")
    replaces: list[str] = Field(description="The parts that it replaces")
    review_highlights: list[str] = Field(description="Any interesting highlights about the part from user reviews")
    repair_time: str = Field(description="The repair time of the part")
    installation_directions: str = Field(description="The installation directions of the part. Compile from all installation information available on the part page")
    notes: str = Field(description="Any additional notes about the part")
