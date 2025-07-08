import { EventConfig, Handlers } from 'motia'
import { z } from 'zod'
import axios from 'axios'

const appConfig = require('../config/index.js')

export const config: EventConfig = {
  type: 'event',
  name: 'SchedulePosts',
  description: 'Schedules Twitter and LinkedIn posts using Typefully',
  subscribes: ['schedule-posts'],
  emits: [],
  input: z.object({
    requestId: z.string(),
    url: z.string().url(),
    title: z.string(),
    strategy: z.any(),
    content: z.object({
      twitter: z.any(),
      linkedin: z.any()
    }),
    metadata: z.any(),
    schedulingPreferences: z.object({
      scheduleTwitter: z.boolean(),
      scheduleLinkedIn: z.boolean(),
      twitterScheduleTime: z.string().optional(),
      linkedinScheduleTime: z.string().optional()
    }).optional()
  }),
  flows: ['content-scheduling']
}

export const handler: Handlers['SchedulePosts'] = async (input, { emit, logger }) => {
  logger.info(`📅 Scheduling social media posts for: ${input.title}`)

  const preferences = input.schedulingPreferences || {
    scheduleTwitter: true,
    scheduleLinkedIn: true
  }

  const typefullyHeaders = {
    'X-API-KEY': `Bearer ${appConfig.typefully.apiKey}`,
    'Content-Type': 'application/json'
  }

  // Schedule Twitter content if requested
  if (preferences.scheduleTwitter) {
    const twitterTweets = input.content.twitter.tweets.map((tweet: any) => tweet.text)
    const twitterScheduleTime = preferences.twitterScheduleTime 
      ? new Date(preferences.twitterScheduleTime).toISOString()
      : new Date(Date.now() + 60 * 60 * 1000).toISOString() // Default: 1 hour from now

    const twitterScheduleResponse = await axios.post('https://api.typefully.com/v1/drafts/', {
      content: twitterTweets.join('\n\n\n\n'),
      schedule_date: twitterScheduleTime,
      auto_retweet_enabled: false
    }, { headers: typefullyHeaders })

    logger.info(`🐦 Scheduled Twitter thread for ${preferences.twitterScheduleTime}`)
  } 
  else {
    logger.info(`🐦 Twitter scheduling skipped by user`)
  }

  // Schedule LinkedIn content if requested
  if (preferences.scheduleLinkedIn) {
    const linkedinScheduleTime = preferences.linkedinScheduleTime
      ? new Date(preferences.linkedinScheduleTime).toISOString()
      : new Date(Date.now() + 2 * 60 * 60 * 1000).toISOString() // Default: 2 hours from now

    const linkedinScheduleResponse = await axios.post('https://api.typefully.com/v1/drafts/', {
      content: input.content.linkedin.post,
      schedule_date: linkedinScheduleTime,
      auto_retweet_enabled: false
    }, { headers: typefullyHeaders })

    logger.info(`💼 Scheduled LinkedIn post for ${preferences.linkedinScheduleTime}`)
  } 
  else {
    logger.info(`💼 LinkedIn scheduling skipped by user`)
  }

  await emit({
    topic: 'content-complete',
    data: {
      ...input,
      scheduledAt: new Date().toISOString(),
      schedulingPreferences: preferences
    }
  })
  logger.info(`\n✅ Content scheduling completed successfully!\n`)
}
