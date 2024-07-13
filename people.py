from aiohttp import ClientSession
from asyncio import gather


async def make_request(session: ClientSession, url: str, only_name = False):
    print(f'\nURL:\n{url}')
    async with session.get(url) as response:
        response_dict: dict = await response.json()
        if only_name:
            return response_dict.get("name") or response_dict.get("title")
        else:
            return response_dict


class SwapiAPI():
    
    def __init__(self, no_need_fields: list[str], field_names_with_url: list[str]) -> None:
        self.no_need_fields: list[str] = no_need_fields
        self.field_names_with_url: list[str] = field_names_with_url
    
    
    async def get_all_people(self, async_http_session) -> list[dict]:
        first_people_response = await make_request(async_http_session, 'https://swapi.dev/api/people')
        pages_summary, fractional_part = divmod(first_people_response.get("count"),
                                                len(first_people_response.get("results")))
        pages_summary += 2 if fractional_part > 0 else 1
        pack_people_promises = [make_request(async_http_session, f'https://swapi.dev/api/people/?page={index}')
                                for index in range(2, pages_summary)]
        pages: list[dict] = await gather(*pack_people_promises)
        pages.append(first_people_response)
        return pages
    
    
    @staticmethod
    def clear_people(no_need_fields, people):
        for field in no_need_fields:
            del people[field]
        return people
        

    @staticmethod
    def get_all_links(field_names_with_url, people: dict):
        people_links: dict = {}
        for field in field_names_with_url:
            url = people.get(field)
            if isinstance(url, list):
                if url:
                    for urls in url:
                        people_links[urls] = field
                else:
                    people_links[f'That man does not have {field}'] = field
            elif isinstance(url, str) and url != '':
                people_links[url] = field
        return people, people_links
    

    async def update_people(self, people_with_links: list[tuple[dict, dict[str, str]]], async_http_session) -> list[dict]:
        list_updated_people = []
        for people in people_with_links:
            async_promises = [make_request(async_http_session, url, True) 
                              for url in people[1].keys() if url.startswith('https://')]
            results = await gather(*async_promises)
            
            updated_people = {}
            custom_counter = 0
            for url, field_name in people[1].items():
                if url.startswith('That man does not have'):
                    updated_people[field_name] = url
                else:
                    values = updated_people.get(field_name)
                    if values:
                        updated_people[field_name] = f'{values}, {results[custom_counter]}'
                    else:
                        updated_people[field_name] = results[custom_counter]
                    custom_counter += 1
                        
            people[0].update(updated_people)
            list_updated_people.append(people[0])
        
        return list_updated_people
