require('dotenv').config();

const config = {
  openai: {
    apiKey: process.env.OPENAI_API_KEY,
    model: 'gpt-4o',
  },

  firecrawl: {
    apiKey: process.env.FIRECRAWL_API_KEY,
  },

  motia: {
    port: parseInt(process.env.MOTIA_PORT) || 3000,
  },

  typefully: {
    apiKey: process.env.TYPEFULLY_API_KEY,
  },

  validate() {
    const required = ['OPENAI_API_KEY', 'FIRECRAWL_API_KEY', 'TYPEFULLY_API_KEY'];
    const missing = required.filter(key => !process.env[key]);

    if (missing.length > 0) {
      throw new Error(`Missing required environment variables: ${missing.join(', ')}`);
    }
  }
};

config.validate();

module.exports = config;