# Part 3A - Evaluation Report

## Evaluation Summary

- Total questions: **20**
- Passed: **20**
- Failed: **0**
- Accuracy: **100.0%**
- Unsupported question declined: **True**

## Test Questions

1. How many rooms does plan 12 have?
2. What is the largest room in plan 7?
3. Which plans have more than 3 doors?
4. Which room in plan 4 has no windows?
5. What is the average number of rooms across all plans?
6. How many rooms does plan 1 have?
7. How many doors does plan 4 have?
8. How many windows does plan 7 have?
9. How many walls does plan 12 have?
10. How many rooms does plan 4 have?
11. What is the largest room in plan 4?
12. How many rooms does plan 7 have?
13. What is the largest room in plan 12?
14. How many windows does plan 12 have?
15. How many doors does plan 12 have?
16. How many walls does plan 7 have?
17. How many floor plans are in the dataset?
18. How many components are in the dataset?
19. How many rooms does plan 20 have?
20. How many doors does plan 20 have?

## Failures

None. All evaluation questions passed.

## Unsupported Question Test

Question: `What is the rent for plan 1?`

Declined successfully: **True**

## Evaluation Method

Expected answers were generated using independent SQLite reference queries and compared with the retrieval engine's database evidence.

## Limitations

- Evaluation measures database question-answering accuracy.
- It does not establish that computer-vision room labels are perfect architectural ground truth.
- Room and component classifications are based on heuristic segmentation mappings.
- Pixel area is not equivalent to real-world square footage.
