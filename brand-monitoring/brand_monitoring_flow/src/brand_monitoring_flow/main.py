#!/usr/bin/env python
from pydantic import BaseModel

from crewai.flow import Flow, listen, start
import requests
import asyncio
import time

from brand_monitoring_flow.crews.youtube_crew.youtube_crew import YoutubeCrew, YoutubeReport, YoutubeWriterReport
from brand_monitoring_flow.crews.instagram_crew.instagram_crew import InstagramCrew, InstagramReport, InstagramWriterReport
from brand_monitoring_flow.crews.linkedin_crew.linkedin_crew import LinkedInCrew, LinkedInReport, LinkedInWriterReport
from brand_monitoring_flow.crews.web_crew.web_crew import WebCrew, WebReport, WebWriterReport
from brand_monitoring_flow.crews.X_crew.X_crew import XCrew, XReport, XWriterReport

from brand_monitoring_flow.tools.custom_tool import BrightDataWebSearchTool, scrape_urls
from brand_monitoring_flow.tools.xquik_tool import search_x_mentions

class BrandMonitoringState(BaseModel):
    total_results: int = 15
    brand_name: str = "Browserbase"
    search_response: list[dict] = []

    linkedin_search_response: list[dict] = []
    instagram_search_response: list[dict] = []
    youtube_search_response: list[dict] = []
    web_search_response: list[dict] = []

    linkedin_scrape_response: list[dict] = []
    instagram_scrape_response: list[dict] = []
    youtube_scrape_response: list[dict] = []
    web_scrape_response: list[dict] = []

    linkedin_filtered_scrape_response: list[dict] = []
    instagram_filtered_scrape_response: list[dict] = []
    youtube_filtered_scrape_response: list[dict] = []
    x_filtered_scrape_response: list[dict] = []
    web_filtered_scrape_response: list[dict] = []
    
    linkedin_crew_response: LinkedInReport = None
    instagram_crew_response: InstagramReport = None
    youtube_crew_response: YoutubeReport = None
    x_crew_response: XReport = None
    web_crew_response: WebReport = None

class BrandMonitoringFlow(Flow[BrandMonitoringState]):

    @start()
    def scrape_data(self):
        print(f"Scraping Data about {self.state.brand_name}")
        web_search_tool = BrightDataWebSearchTool()
        self.state.search_response = web_search_tool._run(self.state.brand_name, total_results=self.state.total_results)

        for r in self.state.search_response:
            if "linkedin.com" in r['link'].lower():
                self.state.linkedin_search_response.append(r)
            elif "instagram.com" in r['link'].lower():
                self.state.instagram_search_response.append(r)
            elif "youtube.com" in r['link'].lower():
                self.state.youtube_search_response.append(r)
            elif "x.com" in r['link'].lower() or "twitter.com" in r['link'].lower():
                continue
            else:
                self.state.web_search_response.append(r)

    @listen(scrape_data)
    async def scrape_data_and_analyse(self):

        async def linkedin_analysis():
            if self.state.linkedin_search_response:
                linkedin_urls = [r['link'] for r in self.state.linkedin_search_response]

                print(linkedin_urls)

                linkedin_params = {
                    "dataset_id": "gd_lyy3tktm25m4avu764",
                }

                self.state.linkedin_scrape_response = scrape_urls(linkedin_urls, linkedin_params, "linkedin")

                for i in self.state.linkedin_scrape_response:
                    self.state.linkedin_filtered_scrape_response.append({
                        "url": i["url"],
                        "headline": i["headline"],
                        "post_text": i["post_text"],
                        "hashtags": i["hashtags"],
                        "tagged_companies": i["tagged_companies"],
                        "tagged_people": i["tagged_people"],
                        "original_poster": i["user_id"]
                    })

                linkedin_crew = LinkedInCrew()
                self.state.linkedin_crew_response = linkedin_crew.crew().kickoff(inputs={"linkedin_data": self.state.linkedin_filtered_scrape_response, 
                                                                                "brand_name": self.state.brand_name})
        
        async def instagram_analysis():
            if self.state.instagram_search_response:
                instagram_urls = [r['link'] for r in self.state.instagram_search_response]

                print(instagram_urls)
                insta_params = {
                    "dataset_id": "gd_lk5ns7kz21pck8jpis",
                    "include_errors": "true",
                }

                self.state.instagram_scrape_response = scrape_urls(instagram_urls, insta_params, "instagram")

                for i in self.state.instagram_scrape_response:
                    self.state.instagram_filtered_scrape_response.append({
                        "url": i["url"],
                        "description": i["description"],
                        "likes": i["likes"],
                        "num_comments": i["num_comments"],
                        "is_paid_partnership": i["is_paid_partnership"],
                        "followers": i["followers"],
                        "original_poster": i["user_posted"]
                    })

                instagram_crew = InstagramCrew()
                self.state.instagram_crew_response = instagram_crew.crew().kickoff(inputs={"instagram_data": self.state.instagram_filtered_scrape_response,
                                                                                    "brand_name": self.state.brand_name})

        async def youtube_analysis():
            if self.state.youtube_search_response:
                youtube_urls = [r['link'] for r in self.state.youtube_search_response]

                print(youtube_urls)

                youtube_params = {"dataset_id": "gd_lk56epmy2i5g7lzu0k",
                                "include_errors": "true"} 
                
                self.state.youtube_scrape_response = scrape_urls(youtube_urls, youtube_params, "youtube")

                for i in self.state.youtube_scrape_response:
                    self.state.youtube_filtered_scrape_response.append({
                        "url": i["url"],
                        "title": i["title"],
                        "description": i["description"],
                        "original_poster": i["youtuber"],
                        "verified": i["verified"],
                        "views": i["views"],
                        "likes": i["likes"],
                        "hashtags": i["hashtags"],
                        "transcript": i["transcript"]
                    })

                youtube_crew = YoutubeCrew()
                self.state.youtube_crew_response = youtube_crew.crew().kickoff(inputs={"youtube_data": self.state.youtube_filtered_scrape_response, 
                                                                                "brand_name": self.state.brand_name})

        async def x_analysis():
            self.state.x_filtered_scrape_response = await asyncio.to_thread(
                search_x_mentions,
                self.state.brand_name,
                self.state.total_results,
            )
            if self.state.x_filtered_scrape_response:
                x_crew = XCrew()
                self.state.x_crew_response = x_crew.crew().kickoff(inputs={"x_data": self.state.x_filtered_scrape_response,
                                                                    "brand_name": self.state.brand_name})

        async def web_analysis():
            if self.state.web_search_response:
                web_urls = [r['link'] for r in self.state.web_search_response]

                print(web_urls)

                web_params = {
                    "dataset_id": "gd_m6gjtfmeh43we6cqc",
                    "include_errors": "false",
                    "custom_output_fields": "markdown",
                }

                self.state.web_scrape_response = scrape_urls(web_urls, web_params, "web")

                print(self.state.web_scrape_response)
                print(type(self.state.web_scrape_response))

                for i in self.state.web_scrape_response:
                    self.state.web_filtered_scrape_response.append({
                        "url": i["url"],
                        "markdown": i["markdown"]
                    })

                web_crew = WebCrew()
                self.state.web_crew_response = web_crew.crew().kickoff(inputs={"web_data": self.state.web_filtered_scrape_response,
                                                                               "brand_name": self.state.brand_name})

        tasks = [
            asyncio.create_task(linkedin_analysis()),
            asyncio.create_task(instagram_analysis()),
            asyncio.create_task(youtube_analysis()),
            asyncio.create_task(x_analysis()),
            asyncio.create_task(web_analysis()),
        ]

        await asyncio.gather(*tasks)
        print("Scraping data and analysing complete")

        print("Collected data from all sources")

        if self.state.linkedin_crew_response:   
            for r in self.state.linkedin_crew_response.pydantic.content:
                print(r.post_title)
                print(r.post_link)
                for c in r.content_lines:
                    print("- " + c)
                print("\n")

        if self.state.instagram_crew_response:  
            for r in self.state.instagram_crew_response.pydantic.content:
                print(r.post_title)
                print(r.post_link)
                for c in r.content_lines:
                    print("- " + c)
                print("\n")

        if self.state.youtube_crew_response:
            for r in self.state.youtube_crew_response.pydantic.content:
                print(r.video_title)
                print(r.video_link)
                for c in r.content_lines:
                    print("- " + c)
                print("\n")
        
        if self.state.x_crew_response:
            for r in self.state.x_crew_response.pydantic.content:
                print(r.post_title)
                print(r.post_link)
                for c in r.content_lines:
                    print("- " + c)
                print("\n")

        if self.state.web_crew_response:
            for r in self.state.web_crew_response.pydantic.content:
                print(r.page_title)
                print(r.page_link)
                for c in r.content_lines:
                    print("- " + c)
                print("\n")


def kickoff():
    brand_monitoring_flow = BrandMonitoringFlow()
    brand_monitoring_flow.kickoff()


def plot():
    brand_monitoring_flow = BrandMonitoringFlow()
    brand_monitoring_flow.plot()


if __name__ == "__main__":
    kickoff()
