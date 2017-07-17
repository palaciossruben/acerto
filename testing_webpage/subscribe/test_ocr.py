import pickle
import document_reader
import helper as h


#docs = ['Hoja_de_vida_IEME.pdf']
#folder_path = '../media/resumes/696'
#parsed_filename = '696.txt'
#parsed_path = '../media/resumes/696/696.txt'

#document_reader.read_all_text_and_save(docs, folder_path, parsed_path, parsed_filename)

#docs = ['HV_NICOLAS_BERNAL.jpg']
#folder_path = '../media/resumes/569'
#parsed_filename = '569.txt'
#parsed_path = '../media/resumes/569/569.txt'

#document_reader.read_all_text_and_save(docs, folder_path, parsed_path, parsed_filename)

docs = ['carlos_bejarano.pdf']
folder_path = '../media/resumes/692'
parsed_filename = '692.txt'
parsed_path = '../media/resumes/692/692.txt'

#document_reader.read_all_text_and_save(docs, folder_path, parsed_path, parsed_filename)

relevance_dictionary = pickle.load(open('relevance_dictionary.p', 'rb'))


with open('../media/resumes/632/old.txt', 'r') as f:
    old_relevance = h.get_relevance_index(f.read(), relevance_dictionary)

with open('../media/resumes/632/improved.txt', 'r') as f:
    imp_relevance = h.get_relevance_index(f.read(), relevance_dictionary)

print('OLD RELEVANCE: ' + str(old_relevance))
print('IMPROVED RELEVANCE: ' + str(imp_relevance))
