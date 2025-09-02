
from ..services.event_scraper import scrape_vegas_events
from ..services.geocoder import geocode_address
from ..core.config import settings
import time

# In a real application, you would initialize the Firestore client here.
# from google.cloud import firestore
# db = firestore.Client(project=settings.firestore_project)

def run_event_ingestion():
    """
    Main function for the scheduled job. It scrapes events, geocodes them,
    and saves them to the database.
    """
    print("Starting nightly event ingestion job...")
    
    # 1. Scrape event data from the web
    scraped_events = scrape_vegas_events()
    if not scraped_events:
        print("No events scraped. Job finished.")
        return

    print(f"Successfully scraped {len(scraped_events)} raw event entries.")
    
    enriched_events = []
    for event in scraped_events:
        # 2. Geocode the venue to get lat/lng
        full_address = f"{event.get('venue', '')}, Las Vegas, NV"
        location = geocode_address(full_address)
        
        if location:
            event['lat'] = location['lat']
            event['lng'] = location['lng']
            event['geocode_status'] = 'success'
        else:
            event['geocode_status'] = 'failed'

        enriched_events.append(event)
        
        # Respect rate limits of the geocoding API
        time.sleep(1) 

    print(f"Finished geocoding. {len([e for e in enriched_events if e['geocode_status'] == 'success'])} events successfully located.")

    # 3. Save to Firestore
    # The code below is a placeholder for the actual Firestore integration.
    # In a real implementation, you would use a batch write to efficiently
    # update or create the event documents in Firestore.
    
    print("Simulating write to Firestore...")
    # for event in enriched_events:
    #     doc_ref = db.collection('events').document() # Or use a specific ID
    #     doc_ref.set(event)
    
    print(f"Successfully processed and saved {len(enriched_events)} events.")
    print("Event ingestion job finished.")

if __name__ == '__main__':
    # This allows running the job manually for testing.
    run_event_ingestion()
