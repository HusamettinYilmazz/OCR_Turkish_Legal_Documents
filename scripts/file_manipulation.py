import os
from glob import glob


def fix_files_naming(circulars_dir, decree_files):
    circular_files = glob(os.path.join(circulars_dir, "*.pdf"))
    for idx in range(len(circular_files)):
        new_filename = circular_files[idx].replace("document", "")
        os.rename(circular_files[idx], new_filename)

    decree_files = glob(os.path.join(decrees_dir, "*"))
    for idx in range(len(decree_files)):
        ## delete .pdf if exist for consistent naming
        decree_file_nopdf = decree_files[idx].replace(".pdf", "")
        ## add .pdf for all files
        new_filename = decree_file_nopdf.replace(decree_file_nopdf, f"{decree_file_nopdf}.pdf")
        os.rename(decree_files[idx], new_filename)

def pdf_to_imges(pdf_path, images_path):

    pass

assets_dir = "/home/husammm/Desktop/courses/cs_courses/DL/projects/vlm_ocr_turkish/assets"
circulars_dir = os.path.join(assets_dir, "cumhurbaskanligi_genelgeleri")
decrees_dir = os.path.join(assets_dir, "cumhurbaskanligi_kararnameleri")

if __name__ == "__main__":
    fix_files_naming(circulars_dir, decrees_dir)