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
  name: 'GenerateSocialContent',
  description: 'Generates Twitter and LinkedIn content based on strategy',
  subscribes: ['generate-content'],
  emits: ['content-ready'],
  input: z.object({
    requestId: z.string(),
    url: z.string().url(),
    title: z.string(),
    content: z.string(),
    strategy: z.any(),
    timestamp: z.number()
  }),
  flows: ['content-generation']
}

export const handler: Handlers['GenerateSocialContent'] = async (input, { emit, logger }) => {
  logger.info(`✍️ Generating social media content for: ${input.title}`)

  // Generate Twitter content
  const twitterPromptTemplate = readFileSync(join(__dirname, '../prompts/generate-twitter.txt'), 'utf-8')
  const twitterPrompt = twitterPromptTemplate
    .replace('{{title}}', input.title)
    .replace('{{strategy}}', JSON.stringify(input.strategy.twitterStrategy))
    .replace('{{keyInsights}}', input.strategy.analysis.keyInsights.join(', '))
    .replace('{{format}}', input.strategy.twitterStrategy.format === 'thread' ? 'a Twitter thread (3-5 tweets)' : 'a single engaging tweet')
    .replace('{{targetAudience}}', input.strategy.analysis.targetAudience)

  const twitterResponse = await openai.chat.completions.create({
    model: config.openai.model,
    messages: [{ role: 'user', content: twitterPrompt }],
    temperature: 0.8,
    max_tokens: 800,
    response_format: { type: "json_object" } // explicitly defined for correct parsing
  })

  const twitterContent = JSON.parse(twitterResponse.choices[0].message.content)

  // Generate LinkedIn content
  const linkedinPromptTemplate = readFileSync(join(__dirname, '../prompts/generate-linkedin.txt'), 'utf-8')
  const linkedinPrompt = linkedinPromptTemplate
    .replace('{{title}}', input.title)
    .replace('{{strategy}}', JSON.stringify(input.strategy.linkedinStrategy))
    .replace('{{keyInsights}}', input.strategy.analysis.keyInsights.join(', '))
    .replace('{{targetAudience}}', input.strategy.analysis.targetAudience)

  const linkedinResponse = await openai.chat.completions.create({
    model: config.openai.model,
    messages: [{ role: 'user', content: linkedinPrompt }],
    temperature: 0.7,
    max_tokens: 1000,
    response_format: { type: "json_object" } // explicitly defined for correct parsing
  })

  const linkedinContent = JSON.parse(linkedinResponse.choices[0].message.content)

  logger.info(`🎉 Content generated successfully!`)
  logger.info(`📱 Twitter: ${twitterContent.totalTweets} tweet(s)`)
  logger.info(`💼 LinkedIn: ${linkedinContent.characterCount} characters`)

  await emit({
    topic: 'content-ready',
    data: {
      requestId: input.requestId,
      url: input.url,
      title: input.title,
      strategy: input.strategy,
      content: {
        twitter: twitterContent,
        linkedin: linkedinContent
      },
      metadata: {
        generatedAt: new Date().toISOString(),
        processingTime: Date.now() - input.timestamp,
        targetAudience: input.strategy.analysis.targetAudience
      }
    }
  })
}