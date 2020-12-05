from fpdf import FPDF

def dump_pdf(image_dict, output_file = "../pdf/output_pdf.pdf"):
    pydf = FPDF()
    
        # print (image_info)
    start = image_dict['start']
    end = image_dict['end']
    for page_number in range(start, end + 1):
        pydf.add_page()
        pydf.image(image_dict['name'], x = image_dict['x'], y = image_dict['y'], w = 100)
    pydf.output(output_file)
if __name__ == '__main__':

    image_dict = {'name':'../images/child.png', 'x':100, 'y': 100 ,'start':0, 'end':2}
    dump_pdf(image_dict)