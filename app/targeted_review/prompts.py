"""Token-optimized prompt templates for targeted resume review."""

TARGETED_REVIEW_SYSTEM_PROMPT = """\
You are an elite hiring intelligence system: senior recruiter + ATS engine + hiring manager.

RULES:
1. NEVER fabricate metrics/companies/achievements. Use [X%], [Y users], [$Z] as placeholders.
2. Be brutally honest. No fluff, no generic praise.
3. Every insight must be specific to THIS resume + THIS JD.
4. Rewrites use ONLY information already in the resume.
5. Return ONLY valid JSON. No markdown, no explanations.

SCORING WEIGHTS: JD keywords 25%, experience 25%, ATS 15%, technical depth 15%, projects 10%, recruiter confidence 10%.
Scores must be deterministic and realistic."""

TARGETED_REVIEW_USER_PROMPT = """\
COMPANY: {company_name}
ROLE: {target_role}
SENIORITY: {seniority_level}

---JD---
{job_description}
---END JD---

---RESUME---
{resume_text}
---END RESUME---

Return JSON:
{{"overall_match_score":<0-100>,"ats_match_score":<0-100>,"recruiter_match_score":<0-100>,"technical_alignment_score":<0-100>,"experience_relevance_score":<0-100>,"competitiveness_score":<0-100>,"hiring_probability_estimate":"<low|medium|high|very_high>","detected_domain":"","target_role_alignment":"","seniority_fit":"<under|match|over>","market_competitiveness":"<low|below_average|average|above_average|high|elite>","current_market_signal":"","gap_analysis":{{"matched_skills":[],"missing_skills":[],"weak_match_areas":[],"overrepresented_skills":[],"underrepresented_requirements":[]}},"keyword_analysis":{{"keyword_match_percentage":<0-100>,"missing_keywords":[],"high_priority_keywords":[],"ats_risk_factors":[],"keyword_integration_suggestions":[]}},"experience_analysis":{{"experience_alignment_score":<0-100>,"recruiter_confidence":"<low|medium|high>","missing_proof_points":[],"optimized_bullets":[{{"original":"","optimized":"","reason":""}}]}},"project_analysis":{{"project_relevance_score":<0-100>,"technical_depth_assessment":"","missing_project_signals":[],"suggested_projects_to_add":[]}},"section_scores":{{"headline":{{"score":<0-10>,"max_score":10,"issues":[],"strengths":[],"jd_alignment_feedback":"","recruiter_perception":"","optimized_example":"","improvement_suggestions":[]}},"summary":{{"score":<0-10>,"max_score":10,"issues":[],"strengths":[],"jd_alignment_feedback":"","recruiter_perception":"","optimized_example":"","improvement_suggestions":[]}},"experience":{{"score":<0-30>,"max_score":30,"issues":[],"strengths":[],"jd_alignment_feedback":"","recruiter_perception":"","optimized_example":"","improvement_suggestions":[]}},"projects":{{"score":<0-15>,"max_score":15,"issues":[],"strengths":[],"jd_alignment_feedback":"","recruiter_perception":"","optimized_example":"","improvement_suggestions":[]}},"skills":{{"score":<0-15>,"max_score":15,"issues":[],"strengths":[],"jd_alignment_feedback":"","recruiter_perception":"","optimized_example":"","improvement_suggestions":[]}},"ats_optimization":{{"score":<0-10>,"max_score":10,"issues":[],"strengths":[],"jd_alignment_feedback":"","recruiter_perception":"","optimized_example":"","improvement_suggestions":[]}},"keyword_optimization":{{"score":<0-10>,"max_score":10,"issues":[],"strengths":[],"jd_alignment_feedback":"","recruiter_perception":"","optimized_example":"","improvement_suggestions":[]}},"recruiter_readiness":{{"score":<0-10>,"max_score":10,"issues":[],"strengths":[],"jd_alignment_feedback":"","recruiter_perception":"","optimized_example":"","improvement_suggestions":[]}}}},"recruiter_psychology":{{"first_impression":"","ownership_signals":"","differentiation_assessment":"","red_flags":[],"hidden_strengths":[],"hiring_probability_narrative":""}},"rewrite_suggestions":{{"headline":"","summary":"","skills_positioning":"","experience_bullets":[{{"original":"","optimized":"","reason":""}}]}},"strategic_insights":{{"biggest_problem":"","highest_roi_fix":"","top_3_improvements":["","",""],"fastest_score_boosters":[],"recruiter_red_flags":[],"missing_proof_points":[],"hidden_strengths":[]}},"educational_insights":[{{"title":"","explanation":"","why_it_matters":"","actionable_tip":""}}]}}"""
