from config import mongo_client
from ingest_data import ingest_data
from planning import generate_response
    
if __name__ == "__main__":
    try:
        run_ingest = input("Ingest sample data? (y/n): ")
        if run_ingest.lower() == 'y':
            ingest_data()

        session_id = input("Enter a session ID: ")

        while True:
            user_query = input("\nEnter your query (or type 'quit' to exit): ")
            if user_query.lower() == 'quit':
                break
            
            if not user_query.strip():
                print("Query cannot be empty. Please try again.")
                continue

            answer = generate_response(session_id, user_query)
            print("\nAnswer:")
            print(answer)
    finally:
        mongo_client.close()


