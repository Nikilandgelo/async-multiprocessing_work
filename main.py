import time
from aiohttp import ClientSession
from people import SwapiAPI
from database import init_async_orm, insert_data
from concurrent.futures import Future, ProcessPoolExecutor
from dotenv import find_dotenv, load_dotenv
from asyncio import gather, run, create_task, all_tasks, current_task


async def main():
    start = time.time()
    async with ClientSession() as async_http_session:
        api = SwapiAPI(no_need_fields = ['created', 'edited', 'url'], 
                 field_names_with_url = ['homeworld', 'films', 'species', 'vehicles', 'starships'])
        
        pages: list[dict] = await api.get_all_people(async_http_session)
        session = await init_async_orm()

        async with session() as db_session:
            for page_peoples in pages:
                list_people: list[dict] = page_peoples.get("results")
                with ProcessPoolExecutor(max_workers=len(list_people)) as executor:
                    clean_peoples: list[Future[dict]] = [executor.submit(api.clear_people,
                                               api.no_need_fields, people)
                                               for people in list_people]
                    
                    peoples_links: list[Future[tuple[dict, dict]]] = [executor.submit(api.get_all_links, 
                                                    api.field_names_with_url, clean_people.result())
                                                    for clean_people in clean_peoples]
                    people_links: list[tuple[dict, dict]] = [people_future.result() for people_future in peoples_links]
                    
                updated_peoples: list[dict] = await api.update_people(people_links, async_http_session)  
                create_task(insert_data(updated_peoples, db_session))
            tasks: set = all_tasks()
            tasks.remove(current_task())
            await gather(*tasks)
    print(f'\nOverall time execution is - {round(time.time() - start, 1)}s')


if __name__ == '__main__':
    env_file: str = find_dotenv(".env")
    if env_file != '':
        load_dotenv(env_file)
    
    run(main())