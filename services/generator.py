import asyncio
import logging

from fastapi import logger
from sqlmodel import Session, select
from database import engine
from models import Job, Thumbnail
from services.open_ai_service import generate_image
from services.imagekit_service import upload_file

logger = logging.getLogger(__name__)


STYLES = {
    "bold_dramatic": (
        "Bold and dramatic studio portrait: hard key light from one side, deep shadows, "
        "high contrast (Rembrandt-style lighting), sharp focus on the eyes. "
        "Confident, powerful expression, chin slightly down, direct gaze at camera. "
        "Dark, near-black background with a subtle rim light separating the subject from it. "
        "Shot on an 85mm portrait lens, shallow depth of field."
    ),
    "clean_minimalistic": (
        "Clean, minimalistic corporate headshot: soft, even key light with a large diffused "
        "source (softbox-style), gentle fill, almost no harsh shadows. "
        "Approachable, professional expression with a natural, relaxed smile. "
        "Plain neutral light-grey or white seamless background, evenly lit, no clutter. "
        "Shot on an 85mm portrait lens, shallow depth of field, sharp focus on the eyes."
    ),
    "vibrant_energetic": (
        "Vibrant and energetic headshot: bright, punchy multi-color lighting (gel lighting), "
        "dynamic angle, crisp highlights. "
        "Lively, enthusiastic, friendly expression with genuine energy. "
        "Colorful gradient or bokeh background that complements the subject without "
        "overpowering the face. "
        "Shot on an 85mm portrait lens, shallow depth of field, sharp focus on the eyes."
    ),
}

STYLE_ORDER = ["bold_dramatic", "clean_minimalistic", "vibrant_energetic"]

async def generate_single_thumbnail(thumbnail_id: str, prompt: str, headshot_url: str) -> Thumbnail:
    # DB mark -> generating
    with Session(engine) as session:
        thumb = session.get(Thumbnail, thumbnail_id)
        thumb.status = "generating"
        style_name = thumb.style_name
        session.add(thumb)
        session.commit()

    style_prompt = STYLES[style_name]

    # AI call

    try:
        image_byte = await generate_image(prompt, style_prompt, headshot_url)
        with Session(engine) as session:
            thumb = session.get(Thumbnail, thumbnail_id)
            job_id = thumb.job_id

        # upload to imagekit
        url = upload_file(
            file_bytes=image_byte,
            file_name=f"{thumbnail_id}.png",
            folder=f"thumbnails/{job_id}/",
        )
  

        # db call save to url + mark uploaded
        with Session(engine) as session:
            thumb = session.get(Thumbnail, thumbnail_id)
            thumb.imagekit_url = url
            thumb.status = "uploaded"
            session.add(thumb)
            session.commit()
        logger.info(f"Thumbnail {thumbnail_id} generated and uploaded successfully.")

    except Exception as e:
        logger.error(f"Error generating thumbnail {thumbnail_id}: {e}")
        with Session(engine) as session:
            thumb = session.get(Thumbnail, thumbnail_id)
            thumb.status = "failed"
            thumb.error_message = str(e)[:500]
            session.add(thumb)
            session.commit()


async def process_job(job_id: str):
    # make job as processing 
    # find all thumbnails for the job
    # start one worker for each thumbnail
    # wait for all workers to finish
    # mark job as completed


    with Session(engine) as session:
        job = session.get(Job, job_id)
        job.status = "processing"
        session.add(job)
        session.commit()
        prompt = job.prompt
        headshot_url = job.headshot_url
        thumbnails = session.exec(
            select(Thumbnail).where(Thumbnail.job_id == job_id)
        ).all()
        thumbnail_ids = [thumb.id for thumb in thumbnails]

    tasks = [
        generate_single_thumbnail(thumbnail_id, prompt, headshot_url)
        for thumbnail_id in thumbnail_ids
    ]

    # runs all the tasks concurrently and waits for them to finish
    await asyncio.gather(*tasks)

    with Session(engine) as session:
        thumbnails = session.exec(
            select(Thumbnail).where(Thumbnail.job_id == job_id)
        ).all()
        all_failed = all(t.status == "failed" for t in thumbnails)
        job = session.get(Job, job_id)
        job.status = "failed" if all_failed else "completed"
        session.add(job)
        session.commit()







