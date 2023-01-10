#imports
import numpy as np
import pandas as pd
from rdflib import Graph
from rdflib import URIRef, Literal
from rdflib import Namespace
from rdflib.namespace import OWL, RDF, RDFS, XSD
import streamlit as st

#data
dataframe = pd.read_csv('Webtoon Dataset.csv')
dataframe.at[319,'Writer']= "mame"
st.markdown("**WebToons Data**")
st.dataframe(dataframe)

#creating graph
g = Graph()
g.parse('project ontology.owl', format='xml')
wto = Namespace('http://www.semanticweb.org/WebToons#')
g.bind('wto', wto)

#helping in populating graph
name = dataframe['Name']
name_url = dataframe['Reading Link']
writer = dataframe['Writer']
likes = dataframe['Likes']
genre = dataframe['Genre']
rating = dataframe['Rating']
subscriber = dataframe['Subscribers']
summary = dataframe['Summary']
update = dataframe['Update']

#populating the data
for i in range(len(name_url)):
    if "https:" in name_url[i]:
        #adding the manhwa (the uri being used is informative)
        g.add((URIRef(name_url[i]),RDF.type,URIRef('http://dbpedia.org/resource/Manhwa')))
        g.add((URIRef(name_url[i]),RDFS.label,Literal(name[i], datatype=XSD.string)))
        
        #adding writers of the manhwa
        str_writer = str(writer[i])
        writers = str_writer.split("/")
        for w in writers:
            temp = str(w)
            temp = temp.replace(" ","_")
            temp = URIRef(wto+temp)
            g.add((URIRef(name_url[i]),URIRef('http://dbpedia.org/ontology/writer'),temp))
            g.add((temp,RDFS.label,Literal(str(w), datatype=XSD.string)))
          
        #Adding Total Likes
        l = likes[i]
        if type(l) == str:
            if l.find("M") != -1:
                n,m = l.split("M")
                numb = float(n)*1000000
                g.add((URIRef(name_url[i]),wto.TotalLikes,Literal(numb, datatype=XSD.double)))
            elif l.find("K") != -1:
                n,m = l.split("K")
                numb = float(n)*1000
                g.add((URIRef(name_url[i]),wto.TotalLikes,Literal(numb, datatype=XSD.double)))
        else:
            g.add((URIRef(name_url[i]),wto.TotalLikes,Literal(l, datatype=XSD.double)))
        
        #Adding genre of the webtoon
        g_temp = genre[i]
        g_temp = g_temp.replace(" ","_")
        g.add((URIRef(name_url[i]),URIRef('http://dbpedia.org/ontology/genre'),URIRef(wto+g_temp)))
        g.add((URIRef(wto+g_temp),RDFS.label,Literal(genre[i], datatype=XSD.string)))
        
        #Adding rating
        g.add((URIRef(name_url[i]),wto.rating,Literal(rating[i], datatype=XSD.double)))

        #Adding Total Subscribers
        s = subscriber[i]
        if type(s) == str:
            if s.find("M") != -1:
                n,m = s.split("M")
                numb = float(n)*1000000
                g.add((URIRef(name_url[i]),wto.subscribers,Literal(numb, datatype=XSD.double)))
            elif s.find("K") != -1:
                n,m = s.split("K")
                numb = float(n)*1000
                g.add((URIRef(name_url[i]),wto.subscribers,Literal(numb, datatype=XSD.double)))
        else:
            g.add((URIRef(name_url[i]),wto.subscribers,Literal(s, datatype=XSD.double)))
            
        #Adding webtoon summary/abstract
        g.add((URIRef(name_url[i]),URIRef("http://dbpedia.org/ontology/abstract"),Literal(summary[i], datatype=XSD.string)))
        
        #Weekly schedule
        g.add((URIRef(name_url[i]),wto.WeeklySchedule,Literal(update[i], datatype=XSD.string)))

g.serialize(destination='webtoons.ttl', format='ttl')

g = Graph()
g.parse('webtoons.ttl', format='ttl')

#queries
def Query(g, string):
    result = g.query(string)
    for row in result:
        length = len(row)
        for i in range(length):
            if i == length-1:        
                st.text(row[i])
            else:
                st.text(row[i], end=', ')
#q1
def Query1(g):
    query="""Select Distinct ?name where{
        ?s rdf:type <http://dbpedia.org/resource/Manhwa>;
        rdfs:label ?name.
    }
    """
    Query(g, query)
#q2
def Query2(g):
    query="""Select Distinct ?name where{
        ?s rdf:type <http://dbpedia.org/resource/Manhwa>;
        <http://dbpedia.org/ontology/writer> ?o.
        ?o rdfs:label ?name.
    }
    """
    Query(g, query)
#q3
def Query3(g):
    query="""Select Distinct ?genre where{
        ?s rdf:type <http://dbpedia.org/resource/Manhwa>;
        <http://dbpedia.org/ontology/genre> ?o.
        ?o rdfs:label ?genre.
    }
    """
    Query(g, query)
#q4
def Query4(g, data):
    query=f"""Select ?summary where{{
        ?s rdf:type <http://dbpedia.org/resource/Manhwa>;
        rdfs:label ?name;
        <http://dbpedia.org/ontology/abstract> ?summary;
        Filter(?name = '{data}' ).
    }}
    """
    Query(g, query)
#q5
def Query5(g, data):
    query=f"""Select ?subs where{{
        ?s rdf:type <http://dbpedia.org/resource/Manhwa>;
        rdfs:label ?name;
        wto:subscribers ?subs;
        Filter(?name = '{data}' ).
    }}
    """
    Query(g, query)
#q6
def Query6(g, data):
    query=f"""Select ?likes where{{
        ?s rdf:type <http://dbpedia.org/resource/Manhwa>;
        rdfs:label ?name;
        wto:TotalLikes ?likes;
        Filter(?name = '{data}' ).
    }}
    """
    Query(g, query)
#q7
def Query7(g, data):
    query=f"""Select ?rating where{{
        ?s rdf:type <http://dbpedia.org/resource/Manhwa>;
        rdfs:label ?name;
        wto:rating ?rating;
        Filter(?name = '{data}' ).
    }}
    """
    Query(g, query)
#q8
def Query8(g, data):
    query=f"""Select ?schedule where{{
        ?s rdf:type <http://dbpedia.org/resource/Manhwa>;
        rdfs:label ?name;
        wto:WeeklySchedule ?schedule;
        Filter(?name = '{data}' ).
    }}
    """
    Query(g, query)
#q9
def Query9(g, data):
    query=f"""Select ?s where{{
        ?s rdf:type <http://dbpedia.org/resource/Manhwa>;
        rdfs:label ?name;
        Filter(?name = '{data}').
    }}
    """
    Query(g, query)
#q10
def Query10(g, data):
    data= data.upper()
    query=f"""Select distinct ?name where{{
        ?s rdf:type <http://dbpedia.org/resource/Manhwa>;
        rdfs:label ?name;
        wto:WeeklySchedule ?schedule;
        Filter(?schedule = '{data}' ).
    }}
    """
    Query(g, query)
#q11
def Query11(g, data):
    query=f"""Select ?genre where{{
        ?s rdf:type <http://dbpedia.org/resource/Manhwa>;
        rdfs:label ?name;
        <http://dbpedia.org/ontology/genre> ?o.
        ?o rdfs:label ?genre.
        Filter(?name = '{data}').
    }}
    """
    Query(g, query)
#q12
def Query12(g, data):
    query=f"""Select distinct ?name where{{
        ?s rdf:type <http://dbpedia.org/resource/Manhwa>;
        rdfs:label ?name;
        <http://dbpedia.org/ontology/writer> ?o.
        ?o rdfs:label ?writer.
        Filter(?writer = '{data}' ).
    }}
    """
    Query(g, query)
#q13
def Query13(g):
    query="""
    SELECT ?g (COUNT(?genre) AS ?cnt)
    WHERE {
        ?s <http://dbpedia.org/ontology/genre> ?genre.
        ?genre rdfs:label ?g.

    }
    GROUP BY ?genre
    ORDER BY DESC(?cnt)
    limit 1

    """
    Query(g, query)
#q14
def Query14(g):
    query="""
    SELECT ?g (COUNT(?genre) AS ?cnt)
    WHERE {
        ?s <http://dbpedia.org/ontology/genre> ?genre.
        ?genre rdfs:label ?g.

    }
    GROUP BY ?genre
    ORDER BY DESC(?cnt)
    """
    Query(g, query)
#q15
def Query15(g):
    query="""
    SELECT ?g (SUM(?likes) AS ?cnt)
    WHERE {
        ?s <http://dbpedia.org/ontology/genre> ?genre;
        wto:TotalLikes ?likes.
        ?genre rdfs:label ?g.

    }
    GROUP BY ?genre
    ORDER BY DESC(?cnt)
    limit 1
    """
    Query(g, query)
#q16
def Query16(g):
    query="""
    SELECT ?g (SUM(?likes) AS ?cnt)
    WHERE {
        ?s <http://dbpedia.org/ontology/genre> ?genre;
        wto:TotalLikes ?likes.
        ?genre rdfs:label ?g.

    }
    GROUP BY ?genre
    ORDER BY DESC(?cnt)
    """
    Query(g, query)
#q17
def Query17(g, data):
    query=f"""Select ?maincharacter where{{
        ?s rdf:type <http://dbpedia.org/resource/Manhwa>;
        rdfs:label ?name;
        wto:HasCharacter ?character.
        ?character rdf:type <http://www.semanticweb.org/WebToons#Main_Character>;
        rdfs:label ?maincharacter.
        Filter(?name = '{data}' ).
    }}
    """
    Query(g, query)
#q18
def Query18(g, data):
    query=f"""Select ?maincharacter where{{
        ?s rdf:type <http://dbpedia.org/resource/Manhwa>;
        rdfs:label ?name;
        wto:HasCharacter ?character.
        ?character rdf:type <http://www.semanticweb.org/WebToons#Side_Character>;
        rdfs:label ?maincharacter.
        Filter(?name = '{data}' ).
    }}
    """
    Query(g, query)
#q19
def Query19(g, data1, data2):
    query=f"""Select ?chapter where{{
        ?s rdf:type <http://dbpedia.org/resource/Manhwa>;
        rdfs:label ?name1;
        wto:HasCharacter ?character.
        ?character rdfs:label ?name2.
        ?character <http://www.semanticweb.org/WebToons#FirstAppearance> ?ch.
        ?ch rdfs:label ?chapter.
        Filter(?name1 = '{data1}' && ?name2 ='{data2}').

    }}
    """
    Query(g, query)
#q20
def Query20(g, data1, data2):
    query=f"""Select ?enemy where{{
        ?s rdf:type <http://dbpedia.org/resource/Manhwa>;
        rdfs:label ?name1;
        wto:HasCharacter ?character.
        ?character rdfs:label ?name2.
        ?character <http://www.semanticweb.org/WebToons#Enemy> ?enm.
        ?enm rdfs:label ?enemy.
        Filter(?name1 = '{data1}' && ?name2 ='{data2}').

    }}
    """
    Query(g, query)

st.markdown("**Queries**")
st.markdown("*Press button to run Query*")
st.text(" ")

st.text(" ")
st.markdown("**Get List of all Webtoons**")
q1 = st.button('query 1')
if q1:
    Query1(g)

st.text(" ")
st.text(" ")
st.markdown("**Get List of all Writers**")
q2 = st.button('query 2')
if q2:
    Query2(g)

st.text(" ")
st.text(" ")
st.markdown("**Get List of all Genres**")
q3 = st.button('query 3')
if q3:
    Query3(g)

st.text(" ")
st.text(" ")
st.markdown("**Get summary of Entered Webtoon**")
q4_manhwa_name = st.text_input('q4 Webtoon name')
q4 = st.button('query 4')

if q4:
    Query4(g,q4_manhwa_name)

st.text(" ")
st.text(" ")
st.markdown("**Get Subscribers of Entered Webtoon**")
q5_manhwa_name = st.text_input('q5 Webtoon name')
q5 = st.button('query 5')

if q5:
    Query5(g,q5_manhwa_name)

st.text(" ")
st.text(" ")
st.markdown("**Get Likes of Entered Webtoon**")
q6_manhwa_name = st.text_input('q6 Webtoon name')
q6 = st.button('query 6')

if q6:
    Query6(g,q6_manhwa_name)

st.text(" ")
st.text(" ")
st.markdown("**Get Rating of Entered Webtoon**")
q7_manhwa_name = st.text_input('q7 Webtoon name')
q7 = st.button('query 7')

if q7:
    Query7(g,q7_manhwa_name)

st.text(" ")
st.text(" ")
st.markdown("**Get Schedule of Entered Webtoon**")
q8_manhwa_name = st.text_input('q8 Webtoon name')
q8 = st.button('query 8')

if q8:
    Query8(g,q8_manhwa_name)

st.text(" ")
st.text(" ")
st.markdown("**Get Reading Link of Entered Webtoon**")
q9_manhwa_name = st.text_input('q9 Webtoon name')
q9 = st.button('query 9')

if q9:
    Query9(g,q9_manhwa_name)

st.text(" ")
st.text(" ")
st.markdown("**Get list of Webtoons that are up every X day**")
q10_Xday = st.text_input('q10 Enter Day (Format: UP EVERY <insert day of the week>)')
q10 = st.button('query 10')

if q10:
    Query10(g,q10_Xday)

st.text(" ")
st.text(" ")
st.markdown("**What is the Genre of Entered Webtoon?**")
q11_manhwa_name = st.text_input('q11 Webtoon name')
q11 = st.button('query 11')

if q11:
    Query11(g,q11_manhwa_name)


st.text(" ")
st.text(" ")
st.markdown("**Get names of all Webtoon written by Entered Writer**")
q12_writer_name = st.text_input('q12 writer name')
q12 = st.button('query 12')

if q12:
    Query12(g,q12_writer_name)

st.text(" ")
st.text(" ")
st.markdown("**What Genre of Webtoon is most abundant?**")
q13 = st.button('query 13')
if q13:
    Query13(g)

st.text(" ")
st.text(" ")
st.markdown("**List all genres in descending order based on abundant.**")
q14 = st.button('query 14')
if q14:
    Query14(g)

st.text(" ")
st.text(" ")
st.markdown("**What is the most liked Genre?**")
q15 = st.button('query 15')
if q15:
    Query15(g)

st.text(" ")
st.text(" ")
st.markdown("**Ordered Total likes of all Genres?**")
q16 = st.button('query 16')
if q16:
    Query16(g)

st.text(" ")
st.text(" ")
st.markdown("**Get main character of Entered Webtoon**")
q17_mc_name = st.text_input('q17 main character name')
q17 = st.button('query 17')
if q17:
    Query17(g,q17_mc_name)

st.text(" ")
st.text(" ")
st.markdown("**Get Side character of Entered Webtoon**")
q18_sc_name = st.text_input('q18 side character name')
q18 = st.button('query 18')
if q18:
    Query18(g,q18_sc_name)

st.text(" ")
st.text(" ")
st.markdown("**In which chapter of Entered Webtoon does Entered Character appear for the first time?**")
q19_webtoon_name = st.text_input('q19 webtoon name')
q19_character_name = st.text_input('q19 character name')
q19 = st.button('query 19')
if q19:
    Query19(g,q19_webtoon_name,q19_character_name)

st.text(" ")
st.text(" ")
st.markdown("**Get enemy of Entered Character in Entered Webtoon**")
q20_webtoon_name = st.text_input('q20 webtoon name')
q20_character_name = st.text_input('q20 character name')
q20 = st.button('query 20')
if q20:
    Query20(g,q20_webtoon_name,q20_character_name)




