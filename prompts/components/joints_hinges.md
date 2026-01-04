Component: Joints and hinges

You will be given multiple images in this request:
- Image 1 (QUERY): the inspection photo that must be classified.
- Images 2..N (REFERENCE): preset example photos loaded by the system to illustrate approach damage/conditions.

Important:
- The user uploads only inspection photos. Reference images are NOT user uploads.
- Classify ONLY the QUERY image (Image 1).
- Use REFERENCE images only to calibrate what damage/conditions look like.

Task:
Using the rubric, choose exactly one R_state (R1, R3) for the QUERY image and write a brief reason based on visible evidence in the QUERY image.

Output:
Return ONLY a JSON object that matches the provided JSON schema.
No markdown. No extra keys.
