import { EventConfig, Handlers } from 'motia'
import { z } from 'zod'
import axios from 'axios'

const appConfig = require('../config')

const typefullyApiUrl = 'https://api.typefully.com/v1/drafts/'
const headers = {
  'X-API-KEY': `Bearer ${appConfig.typefully.apiKey}`,
  'Content-Type': 'application/json'
}

export const config: EventConfig = {
  type: 'event',
  name: 'ScheduleLinkedin',
  description: 'Schedules generated LinkedIn post using Typefully',
  subscribes: ['linkedin-schedule'],
  emits: [],
  input: z.object({
    requestId: z.string(),
    url: z.string().url(),
    title: z.string(),
    content: z.any(),
    metadata: z.any()
  }),
  flows: ['content-generation']
}

export const handler: Handlers['ScheduleLinkedin'] = async (input, { emit, state, logger }) => {
  try {
    logger.info(`💼 Scheduling LinkedIn post...`)

    // Convert LinkedIn post to Typefully format
    const linkedinPost = input.content.post

    const linkedinPayload = {
      content: linkedinPost,
      schedule_date: null // Will be posted as draft
    }

    await axios.post(`${typefullyApiUrl}`, linkedinPayload, { headers })

    logger.info(`✅ LinkedIn post scheduled successfully`)
    logger.info(`👀 Visit Typefully to review and publish your content!`)

  } catch (error) {
    logger.error(`❌ LinkedIn post scheduling failed: ${error.message}`)
    throw error
  }
}