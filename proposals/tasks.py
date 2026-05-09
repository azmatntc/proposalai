import json
import logging
import time
from celery import shared_task
from django.core.cache import cache

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3, default_retry_delay=60, name='proposals.tasks.generate_proposal_ai')
def generate_proposal_ai(self, proposal_id: str):
    """Background task for AI proposal generation with caching and retry logic."""
    from .models import Proposal
    from analytics.models import AIUsageLog
    from django.conf import settings

    try:
        proposal = Proposal.objects.select_related('template', 'user').get(id=proposal_id)
    except Proposal.DoesNotExist:
        logger.error(f"Proposal {proposal_id} not found")
        return {'error': 'Proposal not found'}

    user = proposal.user

    # Cache key based on content hash
    import hashlib
    content_hash = hashlib.md5(
        f"{proposal.job_description}{proposal.tone_used}{proposal.client_name}".encode()
    ).hexdigest()
    cache_key = f"proposal_gen:{content_hash}"
    cached_result = cache.get(cache_key)

    if cached_result:
        logger.info(f"Cache hit for proposal {proposal_id}")
        return _apply_result(proposal, cached_result, was_cached=True)

    # Build prompt
    from .prompts import PROPOSAL_GENERATION_SYSTEM_PROMPT, PROPOSAL_USER_PROMPT_TEMPLATE
    import json as json_module

    template_structure = json_module.dumps(
        proposal.template.structure if proposal.template else {
            'sections': [
                {'name': 'greeting'}, {'name': 'understanding'}, {'name': 'approach'},
                {'name': 'experience'}, {'name': 'timeline'}, {'name': 'pricing'}, {'name': 'cta'},
            ]
        }
    )

    user_prompt = PROPOSAL_USER_PROMPT_TEMPLATE.format(
        client_name=proposal.client_name or 'there',
        client_company=proposal.client_company or 'your company',
        job_platform=proposal.get_job_platform_display() if proposal.job_platform else 'Direct',
        tone=proposal.tone_used,
        variables=json_module.dumps(proposal.custom_variables or {}),
        job_description=proposal.job_description[:3000],
        template_structure=template_structure,
    )

    start_time = time.time()
    openai_key = getattr(settings, 'OPENAI_API_KEY', '')

    if not openai_key:
        # Fallback: generate a template-based proposal for dev/demo
        logger.warning("No OpenAI key — using template fallback")
        result = _generate_fallback_proposal(proposal)
    else:
        try:
            import openai
            client = openai.OpenAI(api_key=openai_key)
            response = client.chat.completions.create(
                model=getattr(settings, 'OPENAI_MODEL', 'gpt-4o'),
                messages=[
                    {"role": "system", "content": PROPOSAL_GENERATION_SYSTEM_PROMPT},
                    {"role": "user", "content": user_prompt},
                ],
                response_format={"type": "json_object"},
                temperature=0.7,
                max_tokens=2000,
            )
            raw = json.loads(response.choices[0].message.content)
            generation_time = int((time.time() - start_time) * 1000)
            tokens = response.usage.total_tokens
            cost = (tokens / 1_000_000) * 15.0  # GPT-4o pricing per million tokens

            result = {
                'sections': raw.get('sections', []),
                'metadata': raw.get('metadata', {}),
                'generation_time_ms': generation_time,
                'tokens_used': tokens,
                'cost_usd': cost,
            }
            cache.set(cache_key, result, 3600)

        except openai.RateLimitError as exc:
            raise self.retry(exc=exc, countdown=60 * (2 ** self.request.retries))
        except Exception as exc:
            logger.error(f"AI generation failed: {exc}", exc_info=True)
            result = _generate_fallback_proposal(proposal)

    return _apply_result(proposal, result, was_cached=False)


def _generate_fallback_proposal(proposal):
    """Generate a template-based proposal when AI is unavailable."""
    client = proposal.client_name or 'there'
    company = proposal.client_company or 'your company'
    desc_snippet = proposal.job_description[:200] if proposal.job_description else 'your project'

    sections = [
        {"name": "greeting", "content": f"Hi {client},\n\nI came across your posting and I'm very excited about the opportunity to work with {company}. Your project description immediately caught my attention."},
        {"name": "understanding", "content": f"I understand you're looking for: {desc_snippet}. This is exactly the type of work I specialize in, and I have a clear picture of what you need to achieve."},
        {"name": "approach", "content": "My approach is to start with a thorough discovery phase to ensure we're aligned on requirements, followed by iterative development with regular check-ins. I believe in transparent communication throughout the project."},
        {"name": "experience", "content": "I've successfully delivered similar projects across various industries. My background ensures I can handle the technical challenges and deliver a polished, maintainable solution."},
        {"name": "timeline", "content": "Based on your requirements, I estimate the project can be completed in 2-4 weeks, depending on scope clarification. I'd be happy to break this down into milestones."},
        {"name": "pricing", "content": "My rate is competitive and reflects the quality of work you'll receive. I'm happy to discuss pricing in detail — I offer fixed-price and hourly options depending on your preference."},
        {"name": "cta", "content": f"I'd love to discuss your project further, {client}. Can we schedule a quick call to align on requirements? I'm available this week. Looking forward to potentially working together!"},
    ]

    word_count = sum(len(s['content'].split()) for s in sections)
    return {
        'sections': sections,
        'metadata': {'word_count': word_count, 'estimated_read_time': '2 min', 'confidence_score': 0.7, 'key_phrases_used': []},
        'generation_time_ms': 100,
        'tokens_used': 0,
        'cost_usd': 0.0,
    }


def _apply_result(proposal, result, was_cached=False):
    """Apply generation result to proposal model."""
    from analytics.models import AIUsageLog
    from leads.models import LeadActivity

    sections = result.get('sections', [])
    metadata = result.get('metadata', {})

    proposal.generated_content = {'sections': sections}
    proposal.final_content = '\n\n'.join(s.get('content', '') for s in sections)
    proposal.word_count = metadata.get('word_count') or proposal.get_word_count()
    proposal.generation_time_ms = result.get('generation_time_ms', 0)
    proposal.ai_tokens_used = result.get('tokens_used', 0)
    proposal.ai_cost_usd = result.get('cost_usd', 0.0)
    proposal.status = 'generated'
    proposal.save()

    # Log AI usage
    if result.get('tokens_used', 0) > 0:
        AIUsageLog.objects.create(
            user=proposal.user,
            proposal=proposal,
            model=proposal.ai_model_used,
            prompt_tokens=result['tokens_used'] // 2,
            completion_tokens=result['tokens_used'] // 2,
            total_tokens=result['tokens_used'],
            cost_usd=result['cost_usd'],
            latency_ms=result['generation_time_ms'],
            was_cached=was_cached,
        )

    # Update quota
    proposal.user.increment_proposal_count()

    # Log activity for linked leads
    for lead in proposal.leads.all():
        LeadActivity.objects.create(
            lead=lead, user=proposal.user,
            activity_type='ai_generated',
            description=f'AI proposal generated ({proposal.word_count} words)',
            metadata={'proposal_id': str(proposal.id), 'confidence_score': metadata.get('confidence_score', 0)},
            is_system_generated=True,
        )

    return {
        'proposal_id': str(proposal.id),
        'status': 'completed',
        'word_count': proposal.word_count,
        'cost_usd': float(proposal.ai_cost_usd),
        'was_cached': was_cached,
    }
