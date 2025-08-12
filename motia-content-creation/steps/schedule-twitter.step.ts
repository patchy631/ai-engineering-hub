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
  name: 'ScheduleTwitter',
  description: 'Schedules generated Twitter post using Typefully',
  subscribes: ['twitter-schedule'],
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

export const handler: Handlers['ScheduleTwitter'] = async (input, { emit, state, logger }) => {
  try {
    logger.info(`📱 Scheduling Twitter thread...`)

    // Convert Twitter thread to Typefully format
    const twitterThread = input.content.thread.map((tweet: any) => tweet.content).join('\n\n\n\n')

    const twitterPayload = {
      content: twitterThread,
      schedule_date: null // Will be posted as draft
    }

    await axios.post(`${typefullyApiUrl}`, twitterPayload, { headers })

    logger.info(`✅ Twitter thread scheduled successfully`)
    logger.info(`👀 Visit Typefully to review and publish your content!`)

  } catch (error) {
    logger.error(`❌ Twitter thread scheduling failed: ${error.message}`)
    throw error
  }
}