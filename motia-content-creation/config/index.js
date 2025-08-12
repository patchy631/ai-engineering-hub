require('dotenv').config();

const config = {
  firecrawl: {
    apiKey: process.env.FIRECRAWL_API_KEY,
  },

  typefully: {
    apiKey: process.env.TYPEFULLY_API_KEY,
  },

  validate() {
    const required = ['FIRECRAWL_API_KEY', 'TYPEFULLY_API_KEY'];
    const missing = required.filter(key => !process.env[key]);

    if (missing.length > 0) {
      throw new Error(`Missing required environment variables: ${missing.join(', ')}`);
    }
  }
};

config.validate();

module.exports = config;
