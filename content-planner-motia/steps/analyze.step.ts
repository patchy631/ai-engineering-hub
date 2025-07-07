import { EventConfig, Handlers } from 'motia'
import { z } from 'zod'
import OpenAI from 'openai'
import { readFileSync } from 'fs'
import { join } from 'path'

const config = require('../config') 

const openai = new OpenAI({
  apiKey: config.openai.apiKey,
})

export const config: EventConfig = {
  type: 'event',
  name: 'AnalyzeContent',
  description: 'Analyzes content and creates strategy for social media',
  subscribes: ['analyze-content'],
  emits: ['generate-content'],
  input: z.object({
    requestId: z.string(),
    url: z.string().url(),
    title: z.string(),
    content: z.string(),
    timestamp: z.number()
  }),
  flows: ['content-generation']
}

export const handler: Handlers['AnalyzeContent'] = async (input, { emit, logger }) => {
  logger.info(`🧠 Analyzing content: ${input.title}`)

  const promptTemplate = readFileSync(join(__dirname, '../prompts/analyze-content.txt'), 'utf-8')
  const prompt = promptTemplate
    .replace('{{title}}', input.title)
    .replace('{{content}}', input.content)

  const response = await openai.chat.completions.create({
    model: config.openai.model,
    messages: [{ role: 'user', content: prompt }],
    temperature: 0.7,
    max_tokens: 1500,
    response_format: { type: "json_object" }
  })

  const strategy = JSON.parse(response.choices[0].message.content)

  logger.info(`✅ Strategy created - Target: ${strategy.analysis.targetAudience}`)

  await emit({
    topic: 'generate-content',
    data: {
      requestId: input.requestId,
      url: input.url,
      title: input.title,
      content: input.content,
      strategy,
      timestamp: input.timestamp
    }
  })
}