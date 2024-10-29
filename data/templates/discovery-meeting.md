
### JTBD Interview Notes

## TLDR
- Push Forces: Summarize the main push forces identified
- Pull forces: Summarize the main push forces identified
- Anxieties: Summarize anxieties identified
- Inertia: Summarize inertia identified

**1. Identify Push Forces**
   - **Instructions to LLM:** Look for statements where the customer expresses dissatisfaction or frustration with their current solution. Extract the specific reasons or circumstances that push them toward finding a new solution.
   - **Prompts to Identify Push Forces:**
     - “What made you start looking for a new solution?”
     - “What specific problems or frustrations were you experiencing?”
     - **Output Format for Push Forces:**
       - **Push Force #1:** `[Extracted statement summarizing dissatisfaction or problem]`
       - **Push Force #2:** `[Extracted statement summarizing dissatisfaction or problem]`
       - **Additional Push Forces (if applicable):** `[Extract additional push forces here]`

**2. Identify Pull Forces**
   - **Instructions to LLM:** Capture parts of the conversation where the customer talks about desirable aspects of the new solution or specific benefits they are looking for.
   - **Prompts to Identify Pull Forces:**
     - “What attracted you to this new solution?”
     - “What benefits or improvements were you hoping for with this change?”
     - **Output Format for Pull Forces:**
       - **Pull Force #1:** `[Extracted statement summarizing desirable quality or benefit]`
       - **Pull Force #2:** `[Extracted statement summarizing desirable quality or benefit]`
       - **Additional Pull Forces (if applicable):** `[Extract additional pull forces here]`

**3. Identify Anxieties**
   - **Instructions to LLM:** Focus on parts of the transcription where the customer expresses concerns, doubts, or potential risks about switching to a new solution.
   - **Prompts to Identify Anxieties:**
     - “Were there any concerns or worries when considering this switch?”
     - “What hesitations did you have about changing to this new solution?”
     - **Output Format for Anxieties:**
       - **Anxiety #1:** `[Extracted statement summarizing concern or hesitation]`
       - **Anxiety #2:** `[Extracted statement summarizing concern or hesitation]`
       - **Additional Anxieties (if applicable):** `[Extract additional anxieties here]`

**4. Identify Inertia (Habits)**
   - **Instructions to LLM:** Look for mentions of familiarity, routine, or comfort with the current solution that might contribute to resistance to change.
   - **Prompts to Identify Inertia:**
     - “What aspects of your current solution do you like?”
     - “What made it hard to consider switching to something new?”
     - **Output Format for Inertia:**
       - **Inertia #1:** `[Extracted statement summarizing comfort with current solution]`
       - **Inertia #2:** `[Extracted statement summarizing comfort with current solution]`
       - **Additional Inertia Factors (if applicable):** `[Extract additional inertia factors here]`

---

## Sample Parsing Output

Based on this template, an LLM parsing an interview might output structured insights like:

## TLDR:
- Push Forces: Current tool crashes and makes it hard to share
- Pull forces: Real-time feature and integrations
- Anxieties: Learning curb of new software and compatibility with systems
- Inertia: User is already familiar with existing tool

**Push Forces:**
   - Push Force #1: “The current tool often crashes during busy hours, causing delays.”
   - Push Force #2: “I can’t easily share files with team members using my current system.”

**Pull Forces:**
   - Pull Force #1: “I liked the real-time tracking feature, which could improve my productivity.”
   - Pull Force #2: “The integration with other software I use daily was a big draw.”

**Anxieties:**
   - Anxiety #1: “I was worried that the new system might require a lot of training for my team.”
   - Anxiety #2: “There’s a chance the new tool might not be compatible with my existing software.”

**Inertia:**
   - Inertia #1: “I’ve been using this software for years, and I know all the shortcuts.”
   - Inertia #2: “I’m used to the layout and functionality, even if it’s outdated.”

