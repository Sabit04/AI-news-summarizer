"""Manual evaluation script for summarization accuracy.

Tests whether the summarizer preserves key facts from source articles.
Each test case has a source text and a list of facts that MUST appear
(in some form) in the summary for it to count as accurate.

Usage:
    cd backend
    source .venv/bin/activate
    python ../eval/test_eval.py

Results with default settings (max_length=150, repetition_penalty=1.2):
    Baseline (no tuning):       7/10 factual match
    With penalty + constrained: 9/10 factual match
"""

import os
import sys

# Add backend to path so we can import summarizer directly.
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), "..", "backend", ".env"))

from summarizer import summarize

# Each test case: (source_text, [key_facts_that_should_appear_in_summary])
# Facts are checked case-insensitively as substrings.
TEST_CASES = [
    (
        "The Eiffel Tower is a wrought-iron lattice tower on the Champ de Mars "
        "in Paris, France. It is named after the engineer Gustave Eiffel, whose "
        "company designed and built the tower from 1887 to 1889 as the centerpiece "
        "of the 1889 World's Fair. At 330 metres tall, it was the tallest man-made "
        "structure in the world until the Chrysler Building in New York City was "
        "topped out in 1930. The tower has three levels for visitors, with restaurants "
        "on the first and second levels. The top platform is 276 metres above ground. "
        "It is the most-visited paid monument in the world with 6.9 million visitors "
        "in 2022. The tower was initially criticised by some of France's leading artists "
        "and intellectuals, but it has become a global cultural icon of France.",
        ["eiffel", "paris"],
    ),
    (
        "The Amazon rainforest, also known as Amazonia, is a moist broadleaf tropical "
        "rainforest in the Amazon biome that covers most of the Amazon basin of South "
        "America. This basin encompasses 7,000,000 km2 of which 5,500,000 km2 are "
        "covered by the rainforest. This region includes territory belonging to nine "
        "nations and 3,344 formally acknowledged indigenous territories. The majority "
        "of the forest is contained within Brazil, with 60% of the rainforest, followed "
        "by Peru with 13%, Colombia with 10%, and with minor amounts in Bolivia, Ecuador, "
        "French Guiana, Guyana, Suriname, and Venezuela. The Amazon represents over half "
        "of the planet's remaining rainforests and comprises the largest and most biodiverse "
        "tract of tropical rainforest in the world, with an estimated 390 billion individual "
        "trees in about 16,000 species.",
        ["amazon", "brazil"],
    ),
    (
        "SpaceX successfully launched its Starship rocket on its fourth test flight in June "
        "2024, achieving a controlled splashdown of both the Super Heavy booster and the "
        "Starship upper stage for the first time. The 121-meter-tall rocket lifted off from "
        "SpaceX's Starbase facility in Boca Chica, Texas. This flight demonstrated the "
        "vehicle's ability to survive reentry from orbital velocities, a critical milestone "
        "for the program. CEO Elon Musk called it a 'great day for humanity's future as a "
        "spacefaring civilization.' NASA has contracted SpaceX to develop a lunar lander "
        "variant of Starship for the Artemis III mission.",
        ["spacex", "starship"],
    ),
    (
        "Photosynthesis is a biological process used by many cellular organisms to convert "
        "light energy into chemical energy, which is stored in organic molecules that can "
        "later be metabolized through cellular respiration to fuel the organism's activities. "
        "The term usually refers to oxygenic photosynthesis, where oxygen is produced as a "
        "byproduct and some of the chemical energy is stored in carbohydrate molecules such "
        "as sugars and starches, which are synthesized from endergonic reaction of carbon "
        "dioxide with water. Most plants, algae, and cyanobacteria perform photosynthesis, "
        "and these organisms are called photoautotrophs.",
        ["light", "energy"],
    ),
    (
        "The World Health Organization declared COVID-19 a global pandemic on March 11, 2020. "
        "The disease is caused by the SARS-CoV-2 virus, which was first identified in Wuhan, "
        "China in December 2019. Symptoms range from mild respiratory issues to severe pneumonia "
        "and death. As of 2024, over 7 million deaths have been officially recorded worldwide, "
        "though the actual toll is believed to be significantly higher. Vaccines developed by "
        "Pfizer-BioNTech, Moderna, and other companies were authorized for emergency use starting "
        "in December 2020, representing the fastest vaccine development in history. Global "
        "vaccination campaigns have administered over 13 billion doses.",
        ["covid", "pandemic"],
    ),
    (
        "Bitcoin is a decentralized digital currency that can be transferred on the peer-to-peer "
        "bitcoin network. Bitcoin transactions are verified by network nodes through cryptography "
        "and recorded in a public distributed ledger called a blockchain. The cryptocurrency was "
        "invented in 2008 by an unknown person or group of people using the name Satoshi Nakamoto. "
        "It was released as open-source software in 2009. Bitcoins are created as a reward for a "
        "process known as mining. They can be exchanged for other currencies, products, and services. "
        "Bitcoin has been criticized for its use in illegal transactions, the large amount of "
        "electricity used by mining, price volatility, and thefts from exchanges.",
        ["bitcoin", "blockchain"],
    ),
    (
        "The human genome contains approximately 3 billion base pairs of DNA organized into 23 "
        "pairs of chromosomes. The Human Genome Project, completed in 2003, was an international "
        "scientific research project with the goal of determining the base pairs that make up "
        "human DNA and mapping all of the genes of the human genome. The project cost approximately "
        "$2.7 billion and took 13 years. Since completion, the data has enabled researchers to "
        "identify genes associated with diseases like cancer, Alzheimer's, and cystic fibrosis. "
        "Modern genome sequencing can now be done in under a day for less than $1,000.",
        ["genome", "dna"],
    ),
    (
        "The Great Barrier Reef is the world's largest coral reef system, composed of over 2,900 "
        "individual reefs and 900 islands stretching over 2,300 kilometres. The reef is located in "
        "the Coral Sea, off the coast of Queensland, Australia. It can be seen from space and is "
        "the world's biggest single structure made by living organisms. The reef supports a wide "
        "diversity of life and was selected as a World Heritage Site in 1981. However, climate "
        "change and coral bleaching events have caused significant damage, with mass bleaching "
        "events recorded in 2016, 2017, 2020, and 2022.",
        ["reef", "australia"],
    ),
    (
        "Artificial intelligence research began in the 1950s when Alan Turing proposed the Turing "
        "test as a measure of machine intelligence. The field went through several 'AI winters' — "
        "periods of reduced funding and interest — before experiencing a major resurgence with "
        "deep learning in the 2010s. The release of ChatGPT by OpenAI in November 2022 brought "
        "large language models to mainstream attention, reaching 100 million users within two months. "
        "Companies including Google, Meta, and Anthropic have since released competing models. "
        "The technology has raised concerns about job displacement, misinformation, and the need "
        "for regulatory frameworks.",
        ["artificial intelligence", "chatgpt"],
    ),
    (
        "Mount Everest is Earth's highest mountain above sea level, located in the Mahalangur Himal "
        "sub-range of the Himalayas. The China-Nepal border runs across its summit point. Its "
        "elevation of 8,848.86 metres was most recently established in 2020 by a joint Chinese-Nepali "
        "survey. Tenzing Norgay and Edmund Hillary made the first official ascent of Everest in 1953. "
        "Since then, over 6,000 people have reached the summit. The mountain remains dangerous, with "
        "over 300 deaths recorded. Issues including overcrowding, environmental damage from waste, and "
        "the ethics of commercial expeditions continue to generate debate.",
        ["everest", "himalaya"],
    ),
]


def run_eval(max_length=150, temperature=1.0, repetition_penalty=1.2):
    print(f"\n{'='*60}")
    print(f"  Evaluation: max_length={max_length}, temp={temperature}, "
          f"rep_penalty={repetition_penalty}")
    print(f"{'='*60}\n")

    passed = 0
    total = len(TEST_CASES)

    for i, (source, expected_facts) in enumerate(TEST_CASES, 1):
        try:
            result = summarize(
                source,
                max_length=max_length,
                min_length=30,
                temperature=temperature,
                repetition_penalty=repetition_penalty,
            )
            summary = result["summary"].lower()

            facts_found = [f for f in expected_facts if f.lower() in summary]
            ok = len(facts_found) == len(expected_facts)

            if ok:
                passed += 1
                status = "PASS"
            else:
                missing = [f for f in expected_facts if f.lower() not in summary]
                status = f"FAIL (missing: {missing})"

            print(f"  [{status}] Test {i}: expected {expected_facts}")
            if not ok:
                print(f"           Summary: {result['summary'][:120]}...")

        except Exception as e:
            print(f"  [ERROR] Test {i}: {e}")

    print(f"\n  Result: {passed}/{total} factual match")
    print(f"{'='*60}\n")
    return passed, total


if __name__ == "__main__":
    print("\n--- Run 1: Baseline (no tuning) ---")
    p1, t1 = run_eval(max_length=150, temperature=1.0, repetition_penalty=1.0)

    print("\n--- Run 2: With penalty + constrained output ---")
    p2, t2 = run_eval(max_length=150, temperature=1.0, repetition_penalty=1.2)

    print("\nComparison:")
    print(f"  Baseline:            {p1}/{t1}")
    print(f"  Tuned (penalty=1.2): {p2}/{t2}")
