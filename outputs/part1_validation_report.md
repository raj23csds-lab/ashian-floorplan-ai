# Part 1 - Floor Plan Extraction Validation

## Dataset
- Total plans available: 121
- Total extracted element records: 5160

## Sample Plan Validation

| Plan | Rooms | Doors | Windows | Walls | Elements | Invalid bounding boxes | Rooms without links |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 12 | 12 | 10 | 19 | 55 | 0 | 0 |
| 2 | 12 | 13 | 10 | 19 | 56 | 0 | 0 |
| 3 | 13 | 12 | 14 | 18 | 60 | 0 | 0 |

## Generated Overlays

- `outputs/improved_overlays/plan_1_improved.png`
- `outputs/improved_overlays/plan_2_improved.png`
- `outputs/improved_overlays/plan_3_improved.png`

## Limitations

- Semantic class labels are inferred using colour and component-based heuristics.
- Extracted regions are candidate detections, not manually verified architectural room boundaries.
- Some connected regions may combine multiple functional spaces or include corridors.
- Pixel areas are image-space measurements, not real-world square footage.
- Door/window-to-room links are proximity-based relationships.

## Validation Summary

For Plans 1, 2 and 3, all extracted bounding boxes were within image dimensions.
Every extracted room had at least one recorded relationship.
The generated overlays have the same dimensions as their corresponding original images.

## Additional Validation

- Semantic colour legend: outputs/visualizations/color_legend.png
- Visual comparison: outputs/part1_visual_comparison.png
- Database consistency: All six inferred classes matched the stored component counts and bounding boxes for Plans 1, 2 and 3.
- Room extraction consistency: The extracted room components matched the corresponding colour-derived mask regions for all three sample plans.

Note: These checks validate extraction and database consistency against the supplied masks. They do not independently establish semantic classification accuracy against manually annotated ground truth.



