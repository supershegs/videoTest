import os

def save_chunk_to_temporary_location(self, file_id, chunk_number, chunk):
    temporary_directory = "chunks"
    if not os.path.exists(temporary_directory):
        os.makedirs(temporary_directory)
    chunk_filename = os.path.join(temporary_directory, f"{file_id}_chunk_{chunk_number}")
    with open(chunk_filename, 'wb') as chunk_file:
        chunk_file.write(chunk)

def all_chunks_received(self, file_id, total_chunks):
    temporary_directory = "temporary_chunks"
    chunk_files = os.listdir(temporary_directory)
    file_specific_chunks = [filename for filename in chunk_files if filename.startswith(f"{file_id}_chunk_")]
    return len(file_specific_chunks) == total_chunks


def assemble_file(self, file_id, total_chunks):
    temporary_directory = "temporary_chunks"
    chunk_files = os.listdir(temporary_directory)
    file_specific_chunks = [filename for filename in chunk_files if filename.startswith(f"{file_id}_chunk_")]
    file_specific_chunks.sort(key=lambda x: int(x.split("_")[2]))
    final_file_path = f"final_files/{file_id}.bin"  # Define the path for the final file
    with open(final_file_path, 'wb') as final_file:
        for chunk_filename in file_specific_chunks:
            chunk_path = os.path.join(temporary_directory, chunk_filename)
            with open(chunk_path, 'rb') as chunk_file:
                final_file.write(chunk_file.read())

    # Clean up temporary chunk files
    for chunk_filename in file_specific_chunks:
        chunk_path = os.path.join(temporary_directory, chunk_filename)
        os.remove(chunk_path)
