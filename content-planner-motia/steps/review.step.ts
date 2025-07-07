import { EventConfig, Handlers } from 'motia'
import { z } from 'zod'

export const config: EventConfig = {
  type: 'event',
  name: 'ContentReview',
  description: 'Stores generated content in the state',
  subscribes: ['content-ready'],
  emits: ['content-stored'],
  input: z.object({
    requestId: z.string(),
    url: z.string().url(),
    title: z.string(),
    strategy: z.any(),
    content: z.object({
      twitter: z.any(),
      linkedin: z.any()
    }),
    metadata: z.any()
  }),
  flows: ['content-generation']
}

export const handler: Handlers['ContentReview'] = async (input, { emit, state, logger }) => {
  logger.info(`📋 Content ready for review for request: ${input.requestId}`)

  // Store the content data for later retrieval
  await state.set(`content-${input.requestId}`, 'content-data', input)

  await emit({
    topic: 'content-stored',
    data: {
      requestId: input.requestId,
      title: input.title,
      url: input.url,
    }
  })
}