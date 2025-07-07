import { ApiRouteConfig, Handlers } from 'motia'
import { z } from 'zod'

export const config: ApiRouteConfig = {
  type: 'api',
  name: 'ScheduleContentAPI',
  description: 'Allows user to schedule generated content to Twitter and LinkedIn',
  path: '/schedule-content/:requestId',
  method: 'POST',
  bodySchema: z.object({
    approve: z.boolean(),
    scheduleTwitter: z.boolean().optional().default(true),
    scheduleLinkedIn: z.boolean().optional().default(true),
    twitterScheduleTime: z.string().optional(), // ISO string for custom schedule time
    linkedinScheduleTime: z.string().optional() // ISO string for custom schedule time
  }),
  responseSchema: {
    200: z.object({
      message: z.string(),
      requestId: z.string(),
      scheduled: z.object({
        twitter: z.boolean(),
        linkedin: z.boolean()
      })
    }),
    400: z.object({
      error: z.string()
    }),
    404: z.object({
      error: z.string()
    })
  },
  emits: ['schedule-posts'],
  flows: ['content-scheduling']
}

export const handler: Handlers['ScheduleContentAPI'] = async (req, { emit, state, logger }) => {
  const requestId = req.pathParams.requestId
  const { approve, scheduleTwitter, scheduleLinkedIn, twitterScheduleTime, linkedinScheduleTime } = req.body

  // Retrieve the generated content from state
  const contentData = await state.get(`content-${requestId}`, 'content-data')

  if (!contentData) {
    return {
      status: 404,
      body: {
        error: 'Content not found. Please generate content first.'
      }
    }
  }

  if (!approve) {
    logger.info(`❌ User declined to schedule content for request ${requestId}`)
    return {
      status: 200,
      body: {
        message: 'Content scheduling declined',
        requestId,
        scheduled: {
          twitter: false,
          linkedin: false
        }
      }
    }
  }

  logger.info(`✅ User approved scheduling for request ${requestId}`)

  // Emit scheduling event with user preferences
  await emit({
    topic: 'schedule-posts',
    data: {
      ...contentData,
      schedulingPreferences: {
        scheduleTwitter,
        scheduleLinkedIn,
        twitterScheduleTime,
        linkedinScheduleTime
      }
    }
  })

  return {
    status: 200,
    body: {
      message: 'Content scheduling initiated',
      requestId,
      scheduled: {
        twitter: scheduleTwitter,
        linkedin: scheduleLinkedIn
      }
    }
  }
}