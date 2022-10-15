import logging

import azure.functions as func

from datetime import datetime
from PyPDF2 import PdfReader, PdfFileWriter, PdfFileReader

logger = logging.getLogger('azure')
logger.setLevel(logging.DEBUG)


def read_pdf_and_split(pdf_reader: PdfFileReader, name_part): 
    logging.info(f"PdfSplitFn-Inside read_pdf_and_split")   
    start_page_hint="Page 1 /" 
    output_filename = ''
    file_count = 0
    pdf_writer = PdfFileWriter()

    filename_list = []
    logging.info(f"PdfSplitFn-read_pdf_and_split -No of Pages in the pdf = {pdf_reader.getNumPages()}")  
    for x in range(pdf_reader.getNumPages()):

        page = pdf_reader.pages[x]
        page_text = page.extract_text()    
        # if the hint present in the current page , it is the starting page , create a new file and add this page, else add it to the exising file#
        if start_page_hint in page_text:                
            file_count = file_count+1 
            date_time = datetime.now().strftime("%d_%m_%Y_%H_%M_%S")
            output_filename = '{}_part_{}_{}.pdf'.format(name_part, file_count, date_time)
           
            filename_list.append(output_filename)

            pdf_writer = PdfFileWriter()
            pdf_writer.addPage(pdf_reader.getPage(x))
        else:
            pdf_writer.addPage(pdf_reader.getPage(x))

        with open(output_filename, 'wb') as out:
            pdf_writer.write(out)

        print('File Created with Name: {}'.format(output_filename))
        logging.info(f"PdfSplitFn-File Created with Name: {output_filename}") 
    
    return filename_list


def copy_pdf_azure_storage(outputblob: func.Out[bytes], filename_list ):
    logging.info(f"PdfSplitFn-Inside copy_pdf_azure_storage")
    for pdf_fn in filename_list:
        with open(pdf_fn, 'rb') as out:
            outputblob.upload_blob(out)
            print(str(pdf_fn) +" uploaded successfully into blob storage")
            logging.info(f"PdfSplitFn-{pdf_fn} uploaded successfully into blob storage")
            
    for pdf_fn in filename_list:
        if os.path.exists(pdf_fn):
            os.remove(pdf_fn)
            print(str(pdf_fn) +" file has been deleted successfully")
            logging.info(f"PdfSplitFn-{pdf_fn} file has been deleted successfully")
        else:
            print(str(pdf_fn) +" file does not exist!")
            logging.info(f"PdfSplitFn-{pdf_fn} file does not exist!")


def main(myblob: func.InputStream , outputblob: func.Out[bytes]):
    logging.info(f"PdfSplitFn- Python blob trigger function processed blob \n"
                 f"PdfSplitFn-Name: {myblob.name}\n"
                 f"PdfSplitFn-Blob Size: {myblob.length} bytes")
    blob_bytes = myblob.read()
    blob_to_read = BytesIO(blob_bytes)
    blob_filename = {myblob.name}
    print(blob_filename+" Received in Function App")
    logging.info(f"PdfSplitFn-{blob_filename}  Received in Function App")
    fnameArray = blob_filename.split(".")
    name_part=fnameArray[0]
    file_extenion=fnameArray[1]
    print("File name_part="+name_part+" file_extenion="+file_extenion)
    logging.info(f"PdfSplitFn-File name_part={name_part} file_extenion={file_extenion}")
    #pdf_reader = PdfFileReader(blob_to_read)
    #filename_list = read_pdf_and_split(pdf_reader, name_part)
    #copy_pdf_azure_storage(outputblob,filename_list)

    pdf_reader = PdfFileReader(blob_to_read)
    filename_list = read_pdf_and_split(pdf_reader, name_part)
    copy_pdf_azure_storage(outputblob,filename_list)
    print(blob_filename+" Process completed")
    logging.info(f"PdfSplitFn-{blob_filename} Process completed")

